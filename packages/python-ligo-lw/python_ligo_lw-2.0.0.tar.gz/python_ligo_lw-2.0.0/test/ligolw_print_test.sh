#!/bin/sh

ligolw_print --verbose ligolw_cut_proof.xml | cmp ligolw_print_proof.txt
