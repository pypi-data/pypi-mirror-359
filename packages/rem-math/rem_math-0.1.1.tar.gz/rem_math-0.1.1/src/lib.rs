use numpy::PyReadonlyArray1;
use pyo3::{exceptions, prelude::*};

pub mod native;

#[pyfunction]
#[pyo3(signature = (arr, simd = false))]
pub fn sum_nparr_int32<'py>(
    _py: Python<'py>,
    arr: PyReadonlyArray1<'py, i32>,
    simd: bool,
) -> PyResult<i64> {
    Ok(native::sum_arr_int32(arr.as_slice()?.to_vec(), simd))
}

#[pyfunction]
#[pyo3(signature = (arr, simd = false))]
pub fn sum_arr_int32(_py: Python, arr: Vec<i32>, simd: bool) -> PyResult<i64> {
    Ok(native::sum_arr_int32(arr, simd))
}

#[pyfunction]
#[pyo3(signature = (arr_1, arr_2, simd = false))]
pub fn sum_two_floats32(
    _py: Python,
    arr_1: Vec<f32>,
    arr_2: Vec<f32>,
    simd: bool,
) -> PyResult<Vec<f64>> {
    if arr_1.len() != arr_2.len() {
        return Err(exceptions::PyBaseException::new_err(
            "Array lengths should be equal",
        ));
    }

    Ok(native::sum_two_floats32(arr_1, arr_2, simd))
}

#[pyfunction]
#[pyo3(signature = (arr_1, arr_2, simd = false))]
pub fn sum_two_ints32(
    _py: Python,
    arr_1: Vec<i32>,
    arr_2: Vec<i32>,
    simd: bool,
) -> PyResult<Vec<i64>> {
    if arr_1.len() != arr_2.len() {
        return Err(exceptions::PyBaseException::new_err(
            "Array lengths should be equal",
        ));
    }

    Ok(native::sum_two_ints32(arr_1, arr_2, simd))
}

#[pymodule]
fn rem_math(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_nparr_int32, m)?)?;
    m.add_function(wrap_pyfunction!(sum_arr_int32, m)?)?;
    m.add_function(wrap_pyfunction!(sum_two_floats32, m)?)?;
    m.add_function(wrap_pyfunction!(sum_two_ints32, m)?)?;
    Ok(())
}
