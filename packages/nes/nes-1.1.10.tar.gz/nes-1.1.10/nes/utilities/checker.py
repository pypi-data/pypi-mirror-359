from ..load_nes import open_netcdf
import argparse
from numpy import isinf, isnan

def run_checks():
    parser = argparse.ArgumentParser(description="Check NaN in a NetCDF file.")

    # Define expected arguments
    parser.add_argument("--file", "-f", type=str, help="Input NetCDF file path")
    parser.add_argument("--nan", "-n", type=bool, default=True, help="Check NaNs")
    parser.add_argument("--inf", "-i", type=bool, default=True, help="Check infs")


    # Parse arguments
    args = parser.parse_args()

    # Call your function with parsed arguments
    infile = args.file
    do_nans = args.nan
    do_infs = args.inf

    # Lee solo metadatos
    nessy = open_netcdf(infile)

    # nessy.variables = {'var1': {'data': None, units= kg}}
    # Lee matrices
    nessy.load()
    # nessy.variables = {'var1': {'data': ARRAY, units= kg}}

    for var_name, var_info in nessy.variables.items():
        # var_name = 'var_1'
        # var_info = {'data: np.array, units: 'kg'}
        if do_infs:
            has_inf = isinf(var_info['data']).any()
        else:
            has_inf = False

        if do_nans:
            has_nan = isnan(var_info['data']).any()
        else:
            has_nan = False

        if has_inf or has_nan:
            ValueError(f"{var_name} contains NaN or Inf")
        else:
            pass
    return

# bash_funcion -f -n My_File