use pyo3::{PyErr, PyResult, pyfunction};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;

// Open an HTML in UTF-8 encoding and return a Python string of the contents
#[pyfunction]
pub fn read_html(file_name: &str) -> PyResult<String> {
    let mut file = fs::File::open(file_name).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file: {}", e))
    })?;
    let mut contents = String::new();

    file.read_to_string(&mut contents).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e))
    })?;
    Ok(contents)
}

// Write HTML contents to a file
#[pyfunction]
pub fn write_html(file_name: &str, contents: &str) -> PyResult<()> {
    let mut file = fs::File::create(file_name).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to create file: {}", e))
    })?;

    file.write_all(contents.as_bytes()).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write to file: {}", e))
    })?;

    Ok(())
}

// Write Python bytes to a file
#[pyfunction]
pub fn write_bytes(file_name: &str, contents: &[u8]) -> PyResult<()> {
    let mut file = fs::File::create(file_name).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to create file: {}", e))
    })?;

    file.write_all(contents).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write to file: {}", e))
    })?;

    Ok(())
}

#[derive(Serialize, Deserialize, Debug)]
pub struct BrowserConfig {
    pub(crate) passwords: HashMap<String, [String; 2]>,
    pub(crate) bookmarks: HashMap<String, String>,
    pub(crate) previous_tabs: Vec<String>,
    pub(crate) preferred_browser: String,
    pub(crate) smooth_scrolling: bool,
}

impl Default for BrowserConfig {
    fn default() -> Self {
        BrowserConfig {
            passwords: HashMap::new(),
            bookmarks: HashMap::new(),
            previous_tabs: Vec::new(),
            preferred_browser: String::new(),
            smooth_scrolling: false,
        }
    }
}

fn get_config_path() -> PathBuf {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");

    fs::create_dir_all(&config_dir).expect("Failed to create config dir");

    config_dir.join("config.json")
}

pub fn load_config() -> BrowserConfig {
    let path = get_config_path();
    if !path.exists() {
        save_config(&BrowserConfig::default());
    }

    let mut file = fs::File::open(&path).expect("Failed to open config");
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();

    serde_json::from_str(&contents).unwrap_or_else(|_| BrowserConfig::default())
}

pub fn save_config(config: &BrowserConfig) {
    let path = get_config_path();
    let json = serde_json::to_string_pretty(config).unwrap();
    let mut file = fs::File::create(&path).unwrap();

    file.write_all(json.as_bytes()).unwrap();
}
