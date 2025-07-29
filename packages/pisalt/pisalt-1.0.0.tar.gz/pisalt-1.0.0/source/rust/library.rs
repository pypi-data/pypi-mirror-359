// IMPORT
use pyo3::prelude::*;
mod backend;

// MAIN
#[pymodule]
fn __internal__(module: &Bound<PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(backend::quantum::dsa::bridge::dsakeygen, module)?)?;
    module.add_function(wrap_pyfunction!(backend::quantum::dsa::bridge::dsasign, module)?)?;
    module.add_function(wrap_pyfunction!(backend::quantum::dsa::bridge::dsaverify, module)?)?;
    //
    module.add_function(wrap_pyfunction!(backend::quantum::kem::bridge::kemkeygen, module)?)?;
    module.add_function(wrap_pyfunction!(backend::quantum::kem::bridge::kemencapsulate, module)?)?;
    module.add_function(wrap_pyfunction!(backend::quantum::kem::bridge::kemdecapsulate, module)?)?;
    Ok(())
}
