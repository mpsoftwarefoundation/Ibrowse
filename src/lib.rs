use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;

// Modules
mod framework;
use framework::browser;

// Config
#[derive(Serialize, Deserialize, Debug)]
struct BrowserConfig {
    passwords: HashMap<String, [String; 2]>,
    bookmarks: HashMap<String, String>,
    previous_tabs: Vec<String>,
}

impl Default for BrowserConfig {
    fn default() -> Self {
        BrowserConfig {
            passwords: HashMap::new(),
            bookmarks: HashMap::new(),
            previous_tabs: vec![],
        }
    }
}

// JSON path
fn get_config_path() -> PathBuf {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");

    fs::create_dir_all(&config_dir).expect("Failed to create config dir");

    config_dir.join("config.json")
}

// Load and save
fn load_config() -> BrowserConfig {
    let path = get_config_path();
    if !path.exists() {
        save_config(&BrowserConfig::default());
    }

    let mut file = fs::File::open(&path).expect("Failed to open config");
    let mut contents = String::new();
    file.read_to_string(&mut contents).unwrap();

    serde_json::from_str(&contents).unwrap_or_else(|_| BrowserConfig::default())
}

fn save_config(config: &BrowserConfig) {
    let path = get_config_path();
    let json = serde_json::to_string_pretty(config).unwrap();
    let mut file = fs::File::create(&path).unwrap();
    file.write_all(json.as_bytes()).unwrap();
}

// pyfunctions
#[pyfunction]
fn test() -> PyResult<()> {
    println!("Hello from Rust!");
    Ok(())
}

#[pyfunction]
fn config_dir() -> PyResult<String> {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");
    Ok(config_dir.to_string_lossy().into_owned())
}

#[pyfunction]
fn cache_dir() -> PyResult<String> {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");
    Ok(config_dir.join("cache").to_string_lossy().into_owned())
}

#[pyfunction]
fn passwords() -> PyResult<HashMap<String, [String; 2]>> {
    let config = load_config();
    Ok(config.passwords)
}

#[pyfunction]
fn bookmarks() -> PyResult<HashMap<String, String>> {
    let config = load_config();
    Ok(config.bookmarks)
}

#[pyfunction]
fn previous_tabs() -> PyResult<Vec<String>> {
    let config = load_config();
    Ok(config.previous_tabs)
}

#[pyfunction]
fn add_password(url: &str, username: &str, password: &str) -> PyResult<()> {
    let mut config = load_config();
    let array = [username.to_string(), password.to_string()];
    config.passwords.insert(url.to_string(), array);
    save_config(&config);
    Ok(())
}

#[pyfunction]
fn remove_password(url: &str) -> PyResult<()> {
    let mut config = load_config();
    config.passwords.remove(url);
    save_config(&config);
    Ok(())
}

#[pyfunction]
fn add_bookmark(url: &str, name: &str) -> PyResult<()> {
    let mut config = load_config();
    config.bookmarks.insert(url.to_string(), name.to_string());
    save_config(&config);
    Ok(())
}

#[pyfunction]
fn remove_bookmark(name: &str) -> PyResult<()> {
    let mut config = load_config();
    config.bookmarks.remove(name);
    save_config(&config);
    Ok(())
}

#[pyfunction]
fn set_previous_tabs(tabs: Vec<String>) -> PyResult<()> {
    let mut config = load_config();
    config.previous_tabs = tabs;
    save_config(&config);
    Ok(())
}

// Create the module
#[pymodule]
fn ibrowse(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, py)?)?;
    m.add_function(wrap_pyfunction!(config_dir, py)?)?;
    m.add_function(wrap_pyfunction!(cache_dir, py)?)?;
    m.add_function(wrap_pyfunction!(passwords, py)?)?;
    m.add_function(wrap_pyfunction!(bookmarks, py)?)?;
    m.add_function(wrap_pyfunction!(previous_tabs, py)?)?;
    m.add_function(wrap_pyfunction!(add_password, py)?)?;
    m.add_function(wrap_pyfunction!(remove_password, py)?)?;
    m.add_function(wrap_pyfunction!(add_bookmark, py)?)?;
    m.add_function(wrap_pyfunction!(remove_bookmark, py)?)?;
    m.add_function(wrap_pyfunction!(set_previous_tabs, py)?)?;
    m.add_function(wrap_pyfunction!(framework::browser::clear_caches, py)?)?;
    Ok(())
}
