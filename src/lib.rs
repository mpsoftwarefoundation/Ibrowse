use pyo3::prelude::*;
use pyo3::wrap_pyfunction;



#[pyfunction]
fn test() -> PyResult<()> {
    println!("Hello from rust!");
    Ok(())
}

#[pymodule]
fn ibrowse(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, py)?)?;
    Ok(())
}