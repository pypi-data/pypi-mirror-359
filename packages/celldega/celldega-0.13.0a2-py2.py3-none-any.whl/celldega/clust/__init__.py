"""
Module for clustering high-dimensional data.
"""

# ruff: noqa: E722

# The Celldega Matrix Vizualization Method is being built using the approaches
# and code adaptations from the Clustergrammer-GL library, which is available at
# github.com/ismms-himc/clustergrammer2
# and being used under the license
#
# MIT License

# Copyright (c) 2021 Nicolas Fernandez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import contextlib
from copy import deepcopy
from itertools import combinations
import json
from pathlib import Path
import random

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.stats import mannwhitneyu, ttest_ind
from sklearn.metrics import auc, confusion_matrix, pairwise_distances, roc_curve
import statsmodels.stats.multitest as smm

from . import (
    categories,
    data_formats,
    downsample_fun,
    enrichr_functions as enr_fun,
    export_data,
    iframe_web_app,
    initialize_net,
    load_data,
    load_vect_post,
    make_clust_fun,
    normalize_fun,
    run_filter,
)


def hc(df, filter_n_top=None, norm_col="total", norm_row="zscore"):
    """
    This function performs hierarchical clustering on the rows and columns of a
    DataFrame and returns the visualization JSON for the Celldega-Matrix method.
    This function is developed using the approaches and code adaptations from the
    Clustergrammer2 project.

    Args:
      df (pd.DataFrame): A Pandas DataFrame.
      filter_n_top (int): The number of top dimensions to keep after filtering.
      norm_col (str): The type of normalization to apply to the columns.
      norm_row (str): The type of normalization to apply to the rows.

    Returns:
      dict: The visualization JSON for the Celldega-Matrix method


    Example:
    See [Landscape-Matrix_Xenium](../../../examples/brief_notebooks/Landscape-Matrix_Xenium) notebook.
    """

    net = Network()

    net.load_df(df)

    if filter_n_top is not None:
        net.filter_n_top(axis="row", n_top=5000)

    if norm_col == "total":
        net.normalize(axis="col", norm_type="umi")

    if norm_row == "zscore":
        net.normalize(axis="row", norm_type="zscore")

    net.cluster()

    return net.viz


class Network:
    """
    Clustergrammer.py takes a matrix as input (either from a file of a Pandas DataFrame), normalizes/filters, hierarchically clusters, and produces the :ref:`visualization_json` for :ref:`clustergrammer_js`.

    Networks have two states:

      1. the data state, where they are stored as a matrix and nodes
      2. the viz state where they are stored as viz.links, viz.row_nodes, and viz.col_nodes.

    The goal is to start in a data-state and produce a viz-state of
    the network that will be used as input to clustergram.js.
    """

    def __init__(self, widget=None):
        initialize_net.main(self, widget)

    def reset(self):
        """
        This re-initializes the Network object.
        """
        initialize_net.main(self)

    def load_file(self, filename):
        """
        Load TSV file.
        """
        load_data.load_file(self, filename)

    def load_file_as_string(self, file_string, filename=""):
        """
        Load file as a string.
        """
        load_data.load_file_as_string(self, file_string, filename=filename)

    def load_stdin(self):
        """
        Load stdin TSV-formatted string.
        """
        load_data.load_stdin(self)

    def load_tsv_to_net(self, file_buffer, filename=None):
        """
        This will load a TSV matrix file buffer; this is exposed so that it will
        be possible to load data without having to read from a file.
        """
        load_data.load_tsv_to_net(self, file_buffer, filename)

    def load_vect_post_to_net(self, vect_post):
        """
        Load data in the vector format JSON.
        """
        load_vect_post.main(self, vect_post)

    def load_data_file_to_net(self, filename):
        """
        Load Clustergrammer's dat format (saved as JSON).
        """
        inst_dat = self.load_json_to_dict(filename)
        load_data.load_data_to_net(self, inst_dat)

    def cluster(
        self,
        dist_type="cosine",
        run_clustering=True,
        dendro=True,
        views=None,
        linkage_type="average",
        sim_mat=False,
        filter_sim=0.0,
        calc_cat_pval=False,
        run_enrichr=None,
        enrichrgram=None,
        clust_library="scipy",
        min_samples=1,
        min_cluster_size=2,
    ):
        """
        The main function performs hierarchical clustering, optionally generates
        filtered views (e.g. row-filtered views), and generates the :
        ``visualization_json``.

        Used to set views equal to ['N_row_sum', 'N_row_var']
        """
        if views is None:
            views = []

        initialize_net.viz(self)

        make_clust_fun.make_clust(
            self,
            dist_type=dist_type,
            run_clustering=run_clustering,
            dendro=dendro,
            requested_views=views,
            linkage_type=linkage_type,
            sim_mat=sim_mat,
            filter_sim=filter_sim,
            calc_cat_pval=calc_cat_pval,
            run_enrichr=run_enrichr,
            enrichrgram=enrichrgram,
            clust_library=clust_library,
            min_samples=min_samples,
            min_cluster_size=min_cluster_size,
        )

    def swap_nan_for_zero(self):
        """
        Swaps all NaN (numpy NaN) instances for zero.
        """
        self.dat["mat"][np.isnan(self.dat["mat"])] = 0

    def load_df(
        self,
        df_ini,
        meta_col=None,
        meta_row=None,
        col_cats=None,
        row_cats=None,
        is_downsampled=False,
        meta_ds_row=None,
        meta_ds_col=None,
    ):
        """
        Load Pandas DataFrame.
        """
        self.reset()

        # load dataframe
        df = deepcopy(df_ini)

        if is_downsampled:
            if meta_ds_col is not None:
                self.meta_ds_col = meta_ds_col
            if meta_ds_row is not None:
                self.meta_ds_row = meta_ds_row

        # define downsampled status
        self.is_downsampled = is_downsampled
        # print('load_df: is_downsampled', is_downsampled)

        if not hasattr(self, "meta_col") and not hasattr(self, "meta_row"):
            self.meta_cat = False

        # load metadata
        if isinstance(meta_col, pd.DataFrame):
            self.meta_col = meta_col

            self.col_cats = meta_col.columns.tolist() if col_cats is None else col_cats

            self.meta_cat = True

        if isinstance(meta_row, pd.DataFrame):
            self.meta_row = meta_row

            self.row_cats = meta_row.columns.tolist() if row_cats is None else row_cats

            self.meta_cat = True

        data_formats.df_to_dat(self, df, define_cat_colors=True)

    def export_df(self):
        """
        Export Pandas DataFrame/
        """
        df = data_formats.dat_to_df(self)

        # drop tuple categories if downsampling
        if self.is_downsampled:
            df.columns = self.dat["nodes"]["col"]
            df.index = self.dat["nodes"]["row"]

        return df

    def df_to_dat(self, df, define_cat_colors=False):
        """
        Load Pandas DataFrame (will be deprecated).
        """
        data_formats.df_to_dat(self, df, define_cat_colors)

    def set_matrix_colors(self, pos="red", neg="blue"):
        self.viz["matrix_colors"] = {"pos": pos, "neg": neg}

    def set_global_cat_colors(self, df_meta):
        for inst_name in df_meta.index.tolist():
            inst_color = df_meta.loc[inst_name, "color"]

            self.viz["global_cat_colors"][inst_name] = inst_color

    def set_cat_color(self, axis, cat_index, cat_name, inst_color):
        if axis == 0:
            axis = "row"
        if axis == 1:
            axis = "col"

        with contextlib.suppress(Exception):
            # process cat_index
            cat_index = cat_index - 1
            cat_index = f"cat-{cat_index}"

            self.viz["cat_colors"][axis][cat_index][cat_name] = inst_color

    def dat_to_df(self):
        """
        Export Pandas DataFrams (will be deprecated).
        """
        return data_formats.dat_to_df(self)

    def export_net_json(self, net_type="viz", indent="no-indent"):
        """
        Export dat or viz JSON.
        """
        return export_data.export_net_json(self, net_type, indent)

    def export_viz_to_widget(self, which_viz="viz"):
        """
        Export viz JSON, for use with clustergrammer_widget. Formerly method was
        named widget.
        """

        return export_data.export_net_json(self, which_viz, "no-indent")

    def widget(
        self,
        which_viz="viz",
        link_net=None,
        link_net_js=None,
        clust_library="scipy",
        min_samples=1,
        min_cluster_size=2,
    ):
        """
        Generate a widget visualization using the widget. The export_viz_to_widget
        method passes the visualization JSON to the instantiated widget, which is
        returned and visualized on the front-end.
        """
        # run clustering if necessary
        if len(self.viz["row_nodes"]) == 0:
            self.cluster(
                clust_library=clust_library,
                min_samples=min_samples,
                min_cluster_size=min_cluster_size,
            )

            # add manual_category to viz json
            if "manual_category" in self.dat:
                self.viz["manual_category"] = self.dat["manual_category"]

            # add pre-z-score data to viz
            if "pre_zscore" in self.dat:
                self.viz["pre_zscore"] = self.dat["pre_zscore"]

        self.widget_instance = self.widget_class(network=self.export_viz_to_widget(which_viz))

        # initialize manual category
        if "manual_category" in self.dat:
            manual_cat = {"col": {"col_cat_colors": self.viz["cat_colors"]["col"]["cat-0"]}}

            man_cat_name = self.dat["manual_category"]["col"]
            manual_cat["col"][man_cat_name] = self.meta_col[man_cat_name].to_dict()

            self.widget_instance.manual_cat = json.dumps(manual_cat)

            self.widget_instance.observe(self.get_manual_category, names="manual_cat")

        # add link (python)
        if link_net is not None:
            inst_link = widgets.link(
                (self.widget_instance, "manual_cat"), (link_net.widget_instance, "manual_cat")
            )
            self.widget_instance.link = inst_link

        # add jslink (JavaScript)
        if link_net_js is not None:
            inst_link = widgets.jslink(
                (self.widget_instance, "manual_cat"), (link_net_js.widget_instance, "manual_cat")
            )
            self.widget_instance.link = inst_link

        return self.widget_instance

    def widget_df(self):
        """
        Export a DataFrame from the front-end visualization. For instance, a user
        can filter to show only a single cluster using the dendrogram and then
        get a dataframe of this cluster using the widget_df method.
        """

        if hasattr(self, "widget_instance"):
            if self.widget_instance.mat_string != "":
                tmp_net = deepcopy(Network())

                df_string = self.widget_instance.mat_string

                tmp_net.load_file_as_string(df_string)

                return tmp_net.export_df()

            return self.export_df()

        if hasattr(self, "widget_class"):
            print("Please make the widget before exporting the widget DataFrame.")
            print("Do this using the widget method: net.widget()")
            return None

        print("Can not make widget because Network has no attribute widget_class")
        print(
            "Please instantiate Network with clustergrammer_widget using: Network(clustergrammer_widget)"
        )
        return None

    def write_json_to_file(self, net_type, filename, indent="no-indent"):
        """
        Save dat or viz as a JSON to file.
        """
        export_data.write_json_to_file(self, net_type, filename, indent)

    def write_matrix_to_tsv(self, filename=None, df=None):
        """
        Export data-matrix to file.
        """
        return export_data.write_matrix_to_tsv(self, filename, df)

    def filter_sum(self, threshold, take_abs=True, axis=None, inst_rc=None):
        """
        Filter a network's rows or columns based on the sum across rows or columns.
        """

        if axis is None:
            axis = inst_rc
            print("warning inst_rc argument will be deprecated, please use axis")

            if inst_rc is None:
                print("please provide axis argument")
                return

        inst_df = self.dat_to_df()
        if axis == "row":
            inst_df = run_filter.df_filter_row_sum(inst_df, threshold, take_abs)
        elif axis == "col":
            inst_df = run_filter.df_filter_col_sum(inst_df, threshold, take_abs)
        self.df_to_dat(inst_df)

    def filter_n_top(self, n_top, rank_type="sum", inst_rc=None, axis=None):
        """
        Filter the matrix rows or columns based on sum/variance, and only keep the top
        N.
        """

        if axis is None:
            axis = inst_rc
            print("warning inst_rc argument will be deprecated, please use axis")

            if inst_rc is None:
                print("please provide axis argument")
                return

        inst_df = self.dat_to_df()

        inst_df = run_filter.filter_n_top(inst_rc, inst_df, n_top, rank_type)

        self.df_to_dat(inst_df)

    def filter_threshold(self, threshold, num_occur=1, inst_rc=None, axis=None):
        """
        Filter the matrix rows or columns based on num_occur values being above a
        threshold (in absolute value).
        """

        if axis is None:
            axis = inst_rc
            print("warning inst_rc argument will be deprecated, please use axis")

            if inst_rc is None:
                print("please provide axis argument")
                return

        inst_df = self.dat_to_df()

        inst_df = run_filter.filter_threshold(inst_df, axis, threshold, num_occur)

        self.df_to_dat(inst_df)

    def filter_cat(self, axis, cat_index, cat_name):
        """
        Filter the matrix based on their category. cat_index is the index of the category, the first category has index=1.
        """
        run_filter.filter_cat(self, axis, cat_index, cat_name)

    def filter_names(self, axis, names):
        """
        Filter the visualization using row/column names. The function takes, axis ('row'/'col') and names, a list of strings.
        """
        run_filter.filter_names(self, axis, names)

    def clip(self, lower=None, upper=None):
        """
        Trim values at input thresholds using pandas function
        """
        df = self.export_df()
        df = df.clip(lower=lower, upper=upper)
        self.load_df(df)

    def normalize(self, df=None, norm_type="zscore", axis="row", z_clip=None):
        """
        Normalize the matrix rows or columns using Z-score (zscore) or Quantile Normalization (qn). Users can optionally pass in a DataFrame to be normalized (and this will be incorporated into the Network object).
        """
        normalize_fun.run_norm(self, df, norm_type, axis, z_clip)

    def downsample(
        self,
        df=None,
        ds_type="kmeans",
        axis="row",
        num_samples=100,
        random_state=1000,
        ds_name="Downsample",
        ds_cluster_name="cluster",
    ):
        """
        Downsample the matrix rows or columns (currently supporting kmeans only). Users can optionally pass in a DataFrame to be downsampled (and this will be incorporated into the network object).
        """
        return downsample_fun.main(
            self, df, ds_type, axis, num_samples, random_state, ds_name, ds_cluster_name
        )

    def random_sample(
        self, num_samples, df=None, replace=False, weights=None, random_state=100, axis="row"
    ):
        """
        Return random sample of matrix.
        """

        if df is None:
            df = self.dat_to_df()

        if axis == "row":
            axis = 0
        if axis == "col":
            axis = 1

        df = self.export_df()
        df = df.sample(
            n=num_samples, replace=replace, weights=weights, random_state=random_state, axis=axis
        )

        self.load_df(df)

    def add_cats(self, axis, cat_data):
        """
        Add categories to rows or columns using cat_data array of objects. Each object in cat_data is a dictionary with one key (category title) and value (rows/column names) that have this category. Categories will be added onto the existing categories and will be added in the order of the objects in the array.

        Example ``cat_data``::


            [
              {
                "title": "First Category",
                "cats": {
                  "true": [
                    "ROS1",
                    "AAK1"
                  ]
                }
              },
              {
                "title": "Second Category",
                "cats": {
                  "something": [
                    "PDK4"
                  ]
                }
              }
            ]


        """
        for inst_data in cat_data:
            categories.add_cats(self, axis, inst_data)

    def iframe_web_app(self, filename=None, width=1000, height=800):
        return iframe_web_app.main(self, filename, width, height)

    def enrichrgram(self, lib, axis="row"):
        """
        Add Enrichr gene enrichment results to your visualization (where your rows
        are genes). Run enrichrgram before clustering to incldue enrichment results
        as row categories. Enrichrgram can also be run on the front-end using the
        Enrichr logo at the top left.

        Set lib to the Enrichr library that you want to use for enrichment analysis.
        Libraries included:

          * ChEA_2016
          * KEA_2015
          * ENCODE_TF_ChIP-seq_2015
          * ENCODE_Histone_Modifications_2015
          * Disease_Perturbations_from_GEO_up
          * Disease_Perturbations_from_GEO_down
          * GO_Molecular_Function_2015
          * GO_Biological_Process_2015
          * GO_Cellular_Component_2015
          * Reactome_2016
          * KEGG_2016
          * MGI_Mammalian_Phenotype_Level_4
          * LINCS_L1000_Chem_Pert_up
          * LINCS_L1000_Chem_Pert_down

        """

        df = self.export_df()
        df, bar_info = enr_fun.add_enrichr_cats(df, axis, lib)
        self.load_df(df)

        self.dat["enrichrgram_lib"] = lib
        self.dat["row_cat_bars"] = bar_info

    @staticmethod
    def load_gmt(filename):
        return load_data.load_gmt(filename)

    @staticmethod
    def load_json_to_dict(filename):
        return load_data.load_json_to_dict(filename)

    @staticmethod
    def save_dict_to_json(inst_dict, filename, indent="no-indent"):
        export_data.save_dict_to_json(inst_dict, filename, indent)

    @staticmethod
    def load_gene_exp_to_df(inst_path):
        """
        Loads gene expression data from 10x in sparse matrix format and returns a
        Pandas dataframe
        """

        from ast import literal_eval as make_tuple

        import pandas as pd
        from scipy import io

        # matrix
        matrix = io.mmread(f"{inst_path}matrix.mtx")
        mat = matrix.todense()

        # genes
        filename = f"{inst_path}genes.tsv"
        with Path.open(filename) as f:
            lines = f.readlines()

        # # add unique id to all genes
        # genes = []
        # unique_id = 0
        # for inst_line in lines:
        #     inst_line = inst_line.strip().split()

        #     if len(inst_line) > 1:
        #       inst_gene = inst_line[1]
        #     else:
        #       inst_gene = inst_line[0]

        #     genes.append(inst_gene + '_' + str(unique_id))
        #     unique_id = unique_id + 1

        # add unique id only to duplicate genes
        ini_genes = []
        for inst_line in lines:
            inst_line = inst_line.strip().split()
            inst_gene = inst_line[1] if len(inst_line) > 1 else inst_line[0]
            ini_genes.append(inst_gene)

        gene_name_count = pd.Series(ini_genes).value_counts()
        duplicate_genes = gene_name_count[gene_name_count > 1].index.tolist()

        dup_index = {}
        genes = []
        for inst_row in ini_genes:
            # add index to non-unique genes
            if inst_row in duplicate_genes:
                # calc_non-unque index
                dup_index[inst_row] = dup_index.get(inst_row, 0) + 1

                new_row = f"{inst_row}_{dup_index[inst_row]}"

            else:
                new_row = inst_row

            genes.append(new_row)

        # barcodes
        filename = f"{inst_path}barcodes.tsv"
        with Path.open(filename) as f:
            lines = f.readlines()

        cell_barcodes = []
        for inst_bc in lines:
            inst_bc = inst_bc.strip().split("\t")

            # remove dash from barcodes if necessary
            if "-" in inst_bc[0]:
                inst_bc[0] = inst_bc[0].split("-")[0]

            cell_barcodes.append(inst_bc[0])

        # parse tuples if necessary
        with contextlib.suppress(Exception):
            cell_barcodes = [make_tuple(x) for x in cell_barcodes]

        with contextlib.suppress(Exception):
            genes = [make_tuple(x) for x in genes]

        # make dataframe
        return pd.DataFrame(mat, index=genes, columns=cell_barcodes)

    @staticmethod
    def save_gene_exp_to_mtx_dir(inst_path, df):
        from scipy import io, sparse

        if not Path.exists(inst_path):
            Path.makedirs(inst_path)

        genes = df.index.tolist()
        barcodes = df.columns.tolist()

        Network.save_list_to_tsv(genes, f"{inst_path}genes.tsv")
        Network.save_list_to_tsv(barcodes, f"{inst_path}barcodes.tsv")

        mat_ge = df.values
        mat_ge_sparse = sparse.coo_matrix(mat_ge)

        io.mmwrite(f"{inst_path}matrix.mtx", mat_ge_sparse)

    @staticmethod
    def save_list_to_tsv(inst_list, filename):
        with Path.open(filename, "w") as f:
            for inst_line in inst_list:
                f.write(f"{inst_line}\n")

    def sim_same_and_diff_category_samples(
        self,
        df,
        cat_index=1,
        dist_type="cosine",
        equal_var=False,
        plot_roc=True,
        precalc_dist=False,
        calc_roc=True,
    ):
        """
        Calculate the similarity of samples from the same and different categories. The
        cat_index gives the index of the category, where 1 in the first category
        """

        cols = df.columns.tolist()

        if isinstance(precalc_dist, bool):
            # compute distnace between rows (transpose to get cols as rows)
            dist_arr = 1 - pdist(df.transpose(), metric=dist_type)
        else:
            dist_arr = precalc_dist

        # generate sample names with categories
        sample_combos = list(combinations(range(df.shape[1]), 2))

        sample_names = [
            f"{ind}_same" if cols[x[0]][cat_index] == cols[x[1]][cat_index] else f"{ind}_different"
            for ind, x in enumerate(sample_combos)
        ]

        ser_dist = pd.Series(data=dist_arr, index=sample_names)

        # find same-cat sample comparisons
        same_cat = [x for x in sample_names if x.split("_")[1] == "same"]

        # find diff-cat sample comparisons
        diff_cat = [x for x in sample_names if x.split("_")[1] == "different"]

        # make series of same and diff category sample comparisons
        ser_same = ser_dist[same_cat]
        ser_same.name = "Same Category"
        ser_diff = ser_dist[diff_cat]
        ser_diff.name = "Different Category"

        sim_dict = {"same": ser_same, "diff": ser_diff}
        roc_data = {}
        pval_dict = {}

        _, pval_dict["ttest"] = ttest_ind(ser_diff, ser_same, equal_var=equal_var)

        _, pval_dict["mannwhitney"] = mannwhitneyu(ser_diff, ser_same)

        if calc_roc:
            # calc AUC
            true_index = list(np.ones(sim_dict["same"].shape[0]))
            false_index = list(np.zeros(sim_dict["diff"].shape[0]))
            y_true = true_index + false_index

            true_val = list(sim_dict["same"].values)
            false_val = list(sim_dict["diff"].values)
            y_score = true_val + false_val

            fpr, tpr, thresholds = roc_curve(y_true, y_score)

            inst_auc = auc(fpr, tpr)

            if plot_roc:
                plt.figure()
                plt.plot(fpr, tpr)
                plt.plot([0, 1], [0, 1], color="navy", linestyle="--")
                plt.figure(figsize=(10, 10))

                print("AUC", inst_auc)

            roc_data = {
                "true": y_true,
                "score": y_score,
                "fpr": fpr,
                "tpr": tpr,
                "thresholds": thresholds,
                "auc": inst_auc,
            }

        return {
            "sim_dict": sim_dict,
            "pval_dict": pval_dict,
            "roc_data": roc_data,
        }

    def generate_signatures(
        self,
        df_data,
        df_meta,
        category_name,
        pval_cutoff=0.05,
        num_top_dims=False,
        verbose=True,
        equal_var=False,
    ):
        """
        Generate signatures for column categories
        T-test is run for each category in a one-vs-all manner. The num_top_dims overrides
        the P-value cutoff.
        """

        df_t = df_data.transpose()

        # remove columns (dimensions) with constant values
        orig_num_cols = df_t.shape[1]
        df_t = df_t.loc[:, (df_t != df_t.iloc[0]).any()]
        if df_t.shape[1] < orig_num_cols:
            print("dropped columns with constant values")

        # make tuple rows
        df_t.index = [(x, df_meta.loc[x, category_name]) for x in df_t.index.tolist()]
        category_level = 1

        df = self.row_tuple_to_multiindex(df_t)

        cell_types = sorted(set(df.index.get_level_values(category_level).tolist()))

        keep_genes = []
        keep_genes_dict = {}
        gene_pval_dict = {}
        all_fold_info = {}

        for inst_ct in cell_types:
            inst_ct_mat = df.xs(key=inst_ct, level=category_level)
            inst_other_mat = df.drop(inst_ct, level=category_level)

            # save mean values and fold change
            fold_info = {
                "cluster_mean": inst_ct_mat.mean(),
                "other_mean": inst_other_mat.mean(),
            }
            fold_info["log2_fold"] = fold_info["cluster_mean"] / fold_info["other_mean"]
            fold_info["log2_fold"] = fold_info["log2_fold"].apply(np.log2)
            all_fold_info[inst_ct] = fold_info

            _, inst_pvals = ttest_ind(inst_ct_mat, inst_other_mat, axis=0, equal_var=equal_var)

            ser_pval = pd.Series(data=inst_pvals, index=df.columns.tolist()).sort_values()

            ser_pval_keep = (
                ser_pval[:num_top_dims] if num_top_dims else ser_pval[ser_pval < pval_cutoff]
            )

            gene_pval_dict[inst_ct] = ser_pval_keep

            inst_keep = ser_pval_keep.index.tolist()
            keep_genes.extend(inst_keep)
            keep_genes_dict[inst_ct] = inst_keep

        keep_genes = sorted(set(keep_genes))

        df_gbm = df.groupby(level=category_level).mean().transpose()

        df_sig = df_gbm.loc[keep_genes]

        if len(keep_genes) == 0 and verbose:
            print("found no informative dimensions")

        df_gene_pval = pd.concat(gene_pval_dict, axis=1, sort=False)

        df_diff = {}
        for inst_col in df_gene_pval:
            inst_pvals = df_gene_pval[inst_col]

            # nans represent dimensions that did not meet pval or top threshold
            inst_pvals = inst_pvals.dropna().sort_values()

            inst_genes = inst_pvals.index.tolist()

            # prevent failure if no cells have this category
            if inst_pvals.shape[0] > 0:
                _, pval_corr = smm.multipletests(inst_pvals, 0.05, method="fdr_bh")[:2]

                ser_pval = pd.Series(data=inst_pvals, index=inst_genes, name="P-values")
                ser_bh_pval = pd.Series(data=pval_corr, index=inst_genes, name="BH P-values")
                ser_log2_fold = all_fold_info[inst_col]["log2_fold"].loc[inst_genes]
                ser_log2_fold.name = "Log2 Fold Change"
                ser_cluster_mean = all_fold_info[inst_col]["cluster_mean"].loc[inst_genes]
                ser_cluster_mean.name = "Cluster Mean"
                ser_other_mean = all_fold_info[inst_col]["other_mean"].loc[inst_genes]
                ser_other_mean.name = "All Other Mean"
                inst_df = pd.concat(
                    [ser_pval, ser_bh_pval, ser_log2_fold, ser_cluster_mean, ser_other_mean], axis=1
                )

                df_diff[inst_col] = inst_df

        return df_sig, df_diff

    def old_generate_signatures(
        self,
        df_ini,
        category_level,
        pval_cutoff=0.05,
        num_top_dims=False,
        verbose=True,
        equal_var=False,
    ):
        """Generate signatures for column categories"""

        # change this to use category name and set caetgory level to 1 always
        ###################################

        df_t = df_ini.transpose()

        # remove columns with constant values
        df_t = df_t.loc[:, (df_t != df_t.iloc[0]).any()]

        df = self.row_tuple_to_multiindex(df_t)

        cell_types = sorted(set(df.index.get_level_values(category_level).tolist()))

        keep_genes = []
        keep_genes_dict = {}
        gene_pval_dict = {}
        all_fold_info = {}

        for inst_ct in cell_types:
            inst_ct_mat = df.xs(key=inst_ct, level=category_level)
            inst_other_mat = df.drop(inst_ct, level=category_level)

            # save mean values and fold change
            fold_info = {
                "cluster_mean": inst_ct_mat.mean(),
                "other_mean": inst_other_mat.mean(),
            }
            fold_info["log2_fold"] = fold_info["cluster_mean"] / fold_info["other_mean"]
            fold_info["log2_fold"] = fold_info["log2_fold"].apply(np.log2)
            all_fold_info[inst_ct] = fold_info

            _, inst_pvals = ttest_ind(inst_ct_mat, inst_other_mat, axis=0, equal_var=equal_var)

            ser_pval = pd.Series(data=inst_pvals, index=df.columns.tolist()).sort_values()

            ser_pval_keep = (
                ser_pval[:num_top_dims] if num_top_dims else ser_pval[ser_pval < pval_cutoff]
            )

            gene_pval_dict[inst_ct] = ser_pval_keep

            inst_keep = ser_pval_keep.index.tolist()
            keep_genes.extend(inst_keep)
            keep_genes_dict[inst_ct] = inst_keep

        keep_genes = sorted(set(keep_genes))

        df_gbm = df.groupby(level=category_level).mean().transpose()
        cols = df_gbm.columns.tolist()
        new_cols = [(inst_col, f"{category_level + 1}: {inst_col}") for inst_col in cols]
        df_gbm.columns = new_cols

        df_sig = df_gbm.loc[keep_genes]

        if len(keep_genes) == 0 and verbose:
            print("found no informative dimensions")

        df_gene_pval = pd.concat(gene_pval_dict, axis=1, sort=False)

        return df_sig, df_gene_pval, all_fold_info

    def predict_cats_from_sigs(
        self,
        df_data_ini,
        df_meta,
        df_sig_ini,
        predict="Predicted Category",
        dist_type="cosine",
        unknown_thresh=-1,
    ):
        """Predict category using signature"""

        keep_rows = df_sig_ini.index.tolist()
        data_rows = df_data_ini.index.tolist()

        common_rows = list(set(data_rows).intersection(keep_rows))

        df_data = deepcopy(df_data_ini.loc[common_rows])
        df_sig = deepcopy(df_sig_ini.loc[common_rows])

        # calculate sim_mat of df_data and df_sig
        cell_types = df_sig.columns.tolist()
        barcodes = df_data.columns.tolist()
        sim_mat = 1 - pairwise_distances(df_sig.transpose(), df_data.transpose(), metric=dist_type)
        df_sim = pd.DataFrame(data=sim_mat, index=cell_types, columns=barcodes).transpose()

        # get the top column value (most similar signature)
        df_sim_top = df_sim.idxmax(axis=1)

        # get the maximum similarity of a cell to a cell type definition
        max_sim = df_sim.max(axis=1)

        unknown_cells = max_sim[max_sim < unknown_thresh].index.tolist()

        # assign unknown cells (need category of same name)
        df_sim_top[unknown_cells] = "Unknown"

        # add predicted category name to top list
        # top_list = df_sim_top.values
        df_sim = df_sim.transpose()

        df_meta[predict] = df_sim_top

        return df_sim, df_meta

    def old_predict_cats_from_sigs(
        self,
        df_data_ini,
        df_sig_ini,
        dist_type="cosine",
        predict_level="Predict Category",
        truth_level=1,
        unknown_thresh=-1,
    ):
        """Predict category using signature"""

        keep_rows = df_sig_ini.index.tolist()
        data_rows = df_data_ini.index.tolist()

        common_rows = list(set(data_rows).intersection(keep_rows))

        df_data = deepcopy(df_data_ini.loc[common_rows])
        df_sig = deepcopy(df_sig_ini.loc[common_rows])

        # calculate sim_mat of df_data and df_sig
        cell_types = df_sig.columns.tolist()
        barcodes = df_data.columns.tolist()
        sim_mat = 1 - pairwise_distances(df_sig.transpose(), df_data.transpose(), metric=dist_type)
        df_sim = pd.DataFrame(data=sim_mat, index=cell_types, columns=barcodes).transpose()

        # get the top column value (most similar signature)
        df_sim_top = df_sim.idxmax(axis=1)

        # get the maximum similarity of a cell to a cell type definition
        max_sim = df_sim.max(axis=1)

        unknown_cells = max_sim[max_sim < unknown_thresh].index.tolist()

        # assign unknown cells (need category of same name)
        df_sim_top[unknown_cells] = "Unknown"

        # add predicted category name to top list
        top_list = df_sim_top.values
        top_list = [f"{predict_level}: {x[0] if isinstance(x, tuple) else x}" for x in top_list]

        # add cell type category to input data
        df_cat = deepcopy(df_data)
        cols = df_cat.columns.tolist()

        # check whether the columns have the true category available
        has_truth = isinstance(cols[0], tuple)

        new_cols = (
            [(*a, b) for a, b in zip(cols, top_list, strict=False)]
            if has_truth
            else list(zip(cols, top_list, strict=False))
        )

        # transfer new categories
        df_cat.columns = new_cols

        # keep track of true and predicted labels
        y_info = {"true": [], "pred": []}

        if has_truth:
            y_info["true"] = [x[truth_level].split(": ")[1] for x in cols]
            y_info["pred"] = [x.split(": ")[1] for x in top_list]

        return df_cat, df_sim.transpose(), y_info

    def assess_prediction(self, df_meta, truth, pred):
        """Generate confusion matrix from y_info"""

        y_info = {
            "true": df_meta[truth].values.tolist(),
            "pred": df_meta[pred].values.tolist(),
        }

        sorted_cats = sorted(set(y_info["true"] + y_info["pred"]))
        conf_mat = confusion_matrix(y_info["true"], y_info["pred"], labels=sorted_cats)

        # true columns and pred rows
        df_conf = pd.DataFrame(conf_mat, index=sorted_cats, columns=sorted_cats).transpose()

        total_correct = np.trace(df_conf)
        total_pred = df_conf.sum().sum()
        fraction_correct = total_correct / float(total_pred)

        # calculate ser_correct
        correct_list = []
        cat_counts = df_conf.sum(axis=0)
        all_cols = df_conf.columns.tolist()
        for inst_cat in all_cols:
            inst_correct = df_conf.loc[inst_cat, inst_cat] / cat_counts[inst_cat]
            correct_list.append(inst_correct)

        ser_correct = pd.Series(data=correct_list, index=all_cols)

        return df_conf, ser_correct, fraction_correct

    def old_confusion_matrix_and_correct_series(self, y_info):
        """Generate confusion matrix from y_info"""

        a = deepcopy(y_info["true"])
        true_count = {i: a.count(i) for i in set(a)}

        a = deepcopy(y_info["pred"])
        pred_count = {i: a.count(i) for i in set(a)}

        sorted_cats = sorted(set(y_info["true"] + y_info["pred"]))
        conf_mat = confusion_matrix(y_info["true"], y_info["pred"], sorted_cats)
        df_conf = pd.DataFrame(conf_mat, index=sorted_cats, columns=sorted_cats)

        total_correct = np.trace(df_conf)
        total_pred = df_conf.sum().sum()
        fraction_correct = total_correct / float(total_pred)

        # calculate ser_correct
        correct_list = []
        cat_counts = df_conf.sum(axis=1)
        all_cols = df_conf.columns.tolist()
        for inst_cat in all_cols:
            inst_correct = df_conf[inst_cat].loc[inst_cat] / cat_counts[inst_cat]
            correct_list.append(inst_correct)

        ser_correct = pd.Series(data=correct_list, index=all_cols)

        populations = {"true": true_count, "pred": pred_count}

        return df_conf, populations, ser_correct, fraction_correct

    def compare_performance_to_shuffled_labels(
        self,
        df_data,
        category_level,
        num_shuffles=100,
        random_seed=99,
        pval_cutoff=0.05,
        dist_type="cosine",
        num_top_dims=False,
        predict_level="Predict Category",
        truth_level=1,
        unknown_thresh=-1,
        equal_var=False,
        performance_type="prediction",
    ):
        random.seed(random_seed)

        perform_list = []

        # pre-calculate the distance matrix (similarity matrix) if necessary
        if performance_type == "cat_sim_auc":
            dist_arr = 1 - pdist(df_data.transpose(), metric=dist_type)

        for inst_run in range(num_shuffles + 1):
            cols = df_data.columns.tolist()
            rows = df_data.index.tolist()
            mat = df_data.values

            shuffled_cols = deepcopy(cols)
            random.shuffle(shuffled_cols)

            # do not perform shuffling the first time to confirm that we get the same
            # results as the unshuffled dataaset
            df_shuffle = (
                deepcopy(df_data)
                if inst_run == 0
                else pd.DataFrame(data=mat, columns=shuffled_cols, index=rows)
            )

            # generate signature on shuffled data
            df_sig, keep_genes, keep_genes_dict, fold_info = self.generate_signatures(
                df_shuffle,
                category_level,
                pval_cutoff=pval_cutoff,
                num_top_dims=num_top_dims,
                equal_var=equal_var,
            )

            # predictive performance
            if performance_type == "prediction":
                # predict categories from signature
                _, _, y_info = self.predict_cats_from_sigs(
                    df_shuffle,
                    df_sig,
                    dist_type=dist_type,
                    predict_level=predict_level,
                    truth_level=truth_level,
                    unknown_thresh=unknown_thresh,
                )

                # calc confusion matrix and performance
                _, _, _, fraction_correct = self.confusion_matrix_and_correct_series(y_info)

                # store performances of shuffles
                if inst_run > 0:
                    perform_list.append(fraction_correct)
                else:
                    real_performance = fraction_correct
                    print(f"performance (fraction correct) of unshuffled: {real_performance}")

            elif performance_type == "cat_sim_auc":
                # predict categories from signature
                sim_data = self.sim_same_and_diff_category_samples(
                    df_shuffle,
                    cat_index=1,
                    plot_roc=False,
                    equal_var=equal_var,
                    precalc_dist=dist_arr,
                )

                # store performances of shuffles
                if inst_run > 0:
                    perform_list.append(sim_data["roc_data"]["auc"])
                else:
                    real_performance = sim_data["roc_data"]["auc"]
                    print(
                        f"performance (category similarity auc) of unshuffled: {sim_data['roc_data']['auc']}"
                    )

        perform_ser = pd.Series(perform_list)

        in_top_fraction = perform_ser[perform_ser > real_performance].shape[0] / num_shuffles
        print(f"real data performs in the top {in_top_fraction * 100}% of shuffled labels\n")

        return perform_ser

    @staticmethod
    def box_scatter_plot(
        df,
        group,
        columns=False,
        rand_seed=100,
        alpha=0.5,
        dot_color="red",
        num_row=None,
        num_col=1,
        figsize=(10, 10),
        start_title="Variable Measurements Across",
        end_title="Groups",
        group_list=False,
    ):
        import matplotlib.pyplot as plt
        import pandas as pd
        from scipy import stats
        # %matplotlib inline

        if not columns:
            columns = df.columns.tolist()

        plt.figure(figsize=figsize)
        figure_title = f"{start_title} {group} {end_title}"
        plt.suptitle(figure_title, fontsize=20)

        # list of arranged dataframes
        dfs = {}

        for col_num, column in enumerate(columns):
            plot_id = col_num + 1

            # group by column name or multiIndex name
            grouped = df.groupby(group) if group in df.columns.tolist() else df.groupby(level=group)

            names, vals = [], []

            column_title = column[0] if isinstance(column, tuple) else column

            for name, subdf in grouped:
                names.append(name)

                inst_ser = subdf[column]

                column_name = f"{column_title}-{name}"

                inst_ser.name = column_name
                vals.append(inst_ser)

                np.random.seed(rand_seed)

            ax = plt.subplot(num_row, num_col, plot_id)

            plt.boxplot(vals, labels=names)

            ngroup = len(vals)

            clevels = np.linspace(0.0, 1.0, ngroup)

            for clevel in clevels:
                xs = np.random.normal(
                    clevels.tolist().index(clevel) + 1,
                    0.04,
                    len(vals[clevels.tolist().index(clevel)]),
                )
                plt.subplot(num_row, num_col, plot_id)
                plt.scatter(xs, vals[clevels.tolist().index(clevel)], c=dot_color, alpha=alpha)

            df_arranged = pd.concat(vals, axis=1)

            # anova
            anova_data = [df_arranged[col].dropna() for col in df_arranged]
            f_val, pval = stats.f_oneway(*anova_data)

            title_text = (
                f"{column_title} P-val: {pval:.2e}"
                if pval < 0.01
                else f"{column_title} P-val: {round(pval * 100000) / 100000}"
            )
            ax.set_title(title_text)

            dfs[column] = df_arranged

        return dfs

    @staticmethod
    def rank_cols_by_anova_pval(
        df,
        group,
        columns=False,
        rand_seed=100,
        alpha=0.5,
        dot_color="red",
        num_row=None,
        num_col=1,
        figsize=(10, 10),
    ):
        import numpy as np
        import pandas as pd
        from scipy import stats

        # import matplotlib.pyplot as plt
        # %matplotlib inline

        if not columns:
            columns = df.columns.tolist()

        # plt.figure(figsize=figsize)

        # list of arranged dataframes
        pval_list = []

        for column in columns:
            # group by column name or multiIndex name
            grouped = df.groupby(group) if group in df.columns.tolist() else df.groupby(level=group)

            names, vals = [], []

            column_title = column[0] if isinstance(column, tuple) else column

            for name, subdf in grouped:
                names.append(name)

                inst_ser = subdf[column]

                column_name = f"{column_title}-{name}"

                inst_ser.name = column_name
                vals.append(inst_ser)

                np.random.seed(rand_seed)

            df_arranged = pd.concat(vals, axis=1)

            # anova
            anova_data = [df_arranged[col].dropna() for col in df_arranged]
            _, pval = stats.f_oneway(*anova_data)

            pval_list.append(pval)

        pval_ser = pd.Series(data=pval_list, index=columns)
        return pval_ser.sort_values(ascending=True)

    def row_tuple_to_multiindex(self, df):
        from copy import deepcopy

        import pandas as pd

        df_mi = deepcopy(df)
        rows = df_mi.index.tolist()
        titles = []
        for inst_part in rows[0]:
            inst_title = inst_part.split(": ")[0] if ": " in inst_part else "Name"
            titles.append(inst_title)

        new_rows = []
        for inst_row in rows:
            inst_row = list(inst_row)
            new_row = []
            for inst_part in inst_row:
                inst_part = inst_part.split(": ")[1] if ": " in inst_part else inst_part
                new_row.append(inst_part)
            new_row = tuple(new_row)
            new_rows.append(new_row)

        df_mi.index = new_rows

        df_mi.index = pd.MultiIndex.from_tuples(df_mi.index, names=titles)

        return df_mi

    def set_cat_colors(self, cat_colors, axis, cat_index, cat_title=False):
        for inst_ct in cat_colors:
            cat_name = f"{cat_title}: {inst_ct}" if cat_title else inst_ct

            inst_color = cat_colors[inst_ct]
            self.set_cat_color(
                axis=axis, cat_index=cat_index, cat_name=cat_name, inst_color=inst_color
            )

    def set_manual_category(self, col=None, row=None, preferred_cats=None):
        """
        This method is used to tell Clustergrammer2 that the user wants to define
        a manual category interactively using the dendrogram.
        """

        self.dat["manual_category"] = {"col": col, "row": row}

        if preferred_cats is not None:
            pref_cats = []
            for inst_row in preferred_cats.index.tolist():
                inst_dict = {
                    "name": inst_row,
                    "color": preferred_cats.loc[inst_row, "color"],
                }
                pref_cats.append(inst_dict)

            if col is not None:
                self.dat["manual_category"]["col_cats"] = pref_cats

            if row is not None:
                self.dat["manual_category"]["row_cats"] = pref_cats

    def ds_to_original_meta(self, axis):
        clusters = self.meta_ds_col.index.tolist()

        man_cat_title = self.dat["manual_category"][axis]

        for inst_cluster in clusters:
            # get the manual category from the downsampled data
            inst_man_cat = self.meta_ds_col.loc[inst_cluster, man_cat_title]

            # find original labels that are assigned to this cluster
            found_labels = self.meta_col[self.meta_col[self.ds_name] == inst_cluster].index.tolist()

            # update manual category
            self.meta_col.loc[found_labels, man_cat_title] = inst_man_cat

    def get_manual_category(self, tmp):
        for axis in ["col"]:
            with contextlib.suppress(Exception):
                ###########################################################

                export_dict = {}

                inst_nodes = self.dat["nodes"][axis]
                # print('get get_manual_category', len(inst_nodes))

                cat_title = self.dat["manual_category"][axis]

                # Category Names
                with contextlib.suppress(Exception):
                    ###########################################################

                    export_dict[cat_title] = pd.Series(
                        json.loads(self.widget_instance.manual_cat)[axis][cat_title]
                    )

                    if hasattr(self, "meta_cat"):
                        if axis == "row":
                            if not self.is_downsampled:
                                self.meta_row.loc[inst_nodes, cat_title] = export_dict[cat_title]
                            else:
                                self.meta_ds_row.loc[inst_nodes, cat_title] = export_dict[cat_title]
                                self.ds_to_original_meta(axis)

                        elif axis == "col":
                            if not self.is_downsampled:
                                # print('> > > > > > > > > > > ')
                                # print(export_dict[cat_title])

                                # print('.. .. .. .. .. .. .. .. .. .. .. .. ')
                                # print(self.meta_col)

                                # # for some reason this is breaking when trying to sync metadata
                                # # switching to slower row based syncing
                                # self.meta_col.loc[inst_nodes, cat_title] = export_dict[cat_title]

                                # manually looping through rows in metadata works
                                for inst_row in export_dict[cat_title].index.tolist():
                                    self.meta_col.loc[inst_row, cat_title] = export_dict[cat_title][
                                        inst_row
                                    ]

                                # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                                # print(self.meta_col)

                            else:
                                self.meta_ds_col.loc[inst_nodes, cat_title] = export_dict[cat_title]
                                self.ds_to_original_meta(axis)

                # Category Colors
                #######################
                export_dict["cat_colors"] = json.loads(self.widget_instance.manual_cat)[
                    "global_cat_colors"
                ]

                # # drop title from category colors
                # export_dict['cat_colors'] = {}
                # for inst_cat in ini_new_colors:
                #   if (': ' in inst_cat):
                #     export_dict['cat_colors'][inst_cat.split(': ')[1]] = ini_new_colors[inst_cat]
                #   else:
                #     export_dict['cat_colors'][inst_cat] = ini_new_colors[inst_cat]

                # if hasattr(self, 'meta_cat') == False:
                #   return export_dict

    @staticmethod
    def umi_norm(df):
        # umi norm
        barcode_umi_sum = df.sum()
        return df.div(barcode_umi_sum)

    @staticmethod
    def make_df_from_cols(cols):
        inst_col = cols[0]

        cat_titles = []
        for inst_info in inst_col[1:]:
            inst_title = inst_info.split(": ")[0]
            cat_titles.append(inst_title)

        clean_cols = []
        for inst_col in cols:
            inst_clean = [info.split(": ", 1)[1] if ": " in info else info for info in inst_col]
            clean_cols.append(tuple(inst_clean))

        df_ini = pd.DataFrame(data=clean_cols).set_index(0)
        mat = df_ini.values
        rows = df_ini.index.tolist()

        return pd.DataFrame(data=mat, index=rows, columns=cat_titles)


def save_list_to_tsv(inst_list, filename):
    with Path.open(filename, "w") as f:
        for inst_line in inst_list:
            f.write(f"{inst_line}\n")


def generate_signatures(
    df_shuffle,
    category_level,
    pval_cutoff=0.05,
    num_top_dims=False,
    equal_var=False,
):
    """Generate signatures for column categories - standalone function"""
    # This is a placeholder implementation - the actual implementation
    # would need to be provided based on the original function
    return None, [], {}, {}
