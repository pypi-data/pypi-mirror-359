pub mod models {
    pub mod fers {
        pub mod fers;
    }
    pub mod imperfections {
        pub mod imperfectioncase;
        pub mod rotationimperfection;
        pub mod translationimperfection;
    }
    pub mod loads {
        pub mod distributedload;
        pub mod loadcase;
        pub mod loadcombination;
        pub mod nodalload;
        pub mod nodalmoment;
    }
    pub mod members {
        pub mod enums;
        pub mod material;
        pub mod member;
        pub mod memberhinge;
        pub mod memberset;
        pub mod section;
        pub mod shapepath;
        pub mod shapecommand;
    }
    pub mod nodes {
        pub mod node;
    }
    pub mod supports {
        pub mod nodalsupport;
        pub mod supportcondition;
    }
    pub mod settings {
        pub mod settings;
        pub mod analysissettings;
        pub mod generalinfo;
    }
    pub mod results {
        pub mod analysisresults;
        pub mod displacement;
        pub mod forces;
        pub mod memberresultmap;
        pub mod results;
        pub mod resultssummary; 
    }
}

pub mod functions;

mod analysis;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

/// This function is what Python code will call: `fers_calculations.calculate_from_json`.
/// We wrap the internal `analysis::calculate_from_json_internal` so it returns a `PyResult<...>`.
#[pyfunction]
fn calculate_from_json(json_data: &str) -> PyResult<String> {
    match analysis::calculate_from_json_internal(json_data) {
        Ok(msg) => Ok(msg),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
    }
}

/// (Optional) Another Python function that accepts a file path.
#[pyfunction]
fn calculate_from_file(path: &str) -> PyResult<String> {
    match analysis::calculate_from_file_internal(path) {
        Ok(msg) => Ok(msg),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e)),
    }
}

/// The `[pymodule]` attribute is what makes this crate a Python module called "fers_calculations".
#[pymodule]
fn fers_calculations(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add our python-callable functions to the module
    m.add_function(wrap_pyfunction!(calculate_from_json, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_from_file, m)?)?;

    Ok(())
}