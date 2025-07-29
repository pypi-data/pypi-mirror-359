use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

mod error;
mod stats;
mod zscore_e;

pub use error::Error;
pub use zscore_e::{ZScoreEParams, ZScoreEResult};

impl From<Error> for PyErr {
    fn from(err: Error) -> PyErr {
        PyValueError::new_err(err.to_string())
    }
}

/// Python wrapper for ZScoreE result
#[pyclass]
pub struct PyZScoreEResult {
    inner: ZScoreEResult,
}

#[pymethods]
impl PyZScoreEResult {
    #[getter]
    fn outlier_indices(&self) -> Vec<usize> {
        self.inner.outlier_indices().to_vec()
    }

    #[getter]
    fn deviations(&self) -> Vec<f64> {
        self.inner.deviations().to_vec()
    }

    #[getter]
    fn upper_limit(&self) -> f64 {
        self.inner.upper_limit()
    }

    #[getter]
    fn lower_limit(&self) -> f64 {
        self.inner.lower_limit()
    }

    #[getter]
    fn is_outlier(&self) -> Vec<bool> {
        self.inner.is_outlier()
    }

    fn __len__(&self) -> usize {
        self.inner.deviations().len()
    }

    fn __repr__(&self) -> String {
        format!(
            "ZScoreEResult(outliers={}, total_points={})",
            self.inner.outlier_indices().len(),
            self.inner.deviations().len()
        )
    }
}

/// Python wrapper for ZScoreE parameters and detection
#[pyclass]
pub struct ZScoreE {
    params: ZScoreEParams,
}

#[pymethods]
impl ZScoreE {
    #[new]
    #[pyo3(signature = (window_percent=0.1, threshold_multiplier=3.0, factor=1.2533))]
    fn new(window_percent: f64, threshold_multiplier: f64, factor: f64) -> PyResult<Self> {
        let mut params = ZScoreEParams::new();
        params
            .window_percent(window_percent)
            .threshold_multiplier(threshold_multiplier)
            .factor(factor);

        Ok(Self { params })
    }

    /// Detect outliers in the given data with GIL release
    fn detect_outliers(&self, py: Python, data: Vec<f64>) -> PyResult<PyZScoreEResult> {
        // Release the GIL during computation
        let result = py.allow_threads(|| self.params.detect_outliers(&data))?;
        Ok(PyZScoreEResult { inner: result })
    }

    #[getter]
    fn window_percent(&self) -> f64 {
        self.params.window_percent
    }

    #[getter]
    fn threshold_multiplier(&self) -> f64 {
        self.params.threshold_multiplier
    }

    #[getter]
    fn factor(&self) -> f64 {
        self.params.factor
    }

    fn __repr__(&self) -> String {
        format!(
            "ZScoreE(window_percent={}, threshold_multiplier={}, factor={})",
            self.params.window_percent, self.params.threshold_multiplier, self.params.factor
        )
    }
}

/// Convenience function for ZScoreE detection with default parameters and GIL release
#[pyfunction]
#[pyo3(signature = (data, window_percent=0.1))]
fn detect_outliers_e(py: Python, data: Vec<f64>, window_percent: f64) -> PyResult<PyZScoreEResult> {
    // Release the GIL during computation
    let result =
        py.allow_threads(|| zscore_e::detect_outliers_e_with_window(&data, window_percent))?;
    Ok(PyZScoreEResult { inner: result })
}

/// Calculate median of a dataset
#[pyfunction]
fn median(py: Python, data: Vec<f64>) -> PyResult<f64> {
    let result = py.allow_threads(|| stats::median(&data))?;
    Ok(result)
}

/// Calculate Median Absolute Deviation (MAD)
#[pyfunction]
#[pyo3(signature = (data, center=None))]
fn mad(py: Python, data: Vec<f64>, center: Option<f64>) -> PyResult<f64> {
    let result = py.allow_threads(|| stats::mad(&data, center))?;
    Ok(result)
}

/// Calculate biweight location (robust central tendency)
#[pyfunction]
#[pyo3(signature = (data, c=None))]
fn biweight_location(py: Python, data: Vec<f64>, c: Option<f64>) -> PyResult<f64> {
    let result = py.allow_threads(|| stats::biweight_location(&data, c))?;
    Ok(result)
}

/// Calculate exponential weighted moving average
#[pyfunction]
#[pyo3(signature = (data, span, adjust=false))]
fn ewma(py: Python, data: Vec<f64>, span: usize, adjust: bool) -> PyResult<Vec<f64>> {
    let result = py.allow_threads(|| stats::ewma(&data, span, adjust))?;
    Ok(result)
}

/// The main Python module
#[pymodule]
fn zscore_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Classes
    m.add_class::<ZScoreE>()?;
    m.add_class::<PyZScoreEResult>()?;

    // Outlier detection functions
    m.add_function(wrap_pyfunction!(detect_outliers_e, m)?)?;

    // Statistical functions
    m.add_function(wrap_pyfunction!(median, m)?)?;
    m.add_function(wrap_pyfunction!(mad, m)?)?;
    m.add_function(wrap_pyfunction!(biweight_location, m)?)?;
    m.add_function(wrap_pyfunction!(ewma, m)?)?;

    // Module metadata
    m.add("__version__", "0.1.1")?;
    m.add("__author__", "Thomas Q")?;

    Ok(())
}
