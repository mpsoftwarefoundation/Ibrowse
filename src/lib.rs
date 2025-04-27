use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;


/*************** Configure JSON structure ***************/
#[derive(Serialize, Deserialize, Debug)]
struct BrowserConfig {
    passwords: HashMap<String, [String; 2]>,
    bookmarks: HashMap<String, String>,
    previous_tabs: Vec<String>,
    preferred_browser: String,
}

impl Default for BrowserConfig {
    fn default() -> Self {
        BrowserConfig {
            passwords: HashMap::new(),
            bookmarks: HashMap::new(),
            previous_tabs: vec![],
            preferred_browser: String::new(),
        }
    }
}

/************** Manage paths and load JSON **************/
fn get_config_path() -> PathBuf {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");

    fs::create_dir_all(&config_dir).expect("Failed to create config dir");

    config_dir.join("config.json")
}

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

/*************** Bind functions to Python ***************/

// Test function to test if the bindings are correct
#[pyfunction]
fn test() -> PyResult<()> {
    println!("Hello from Rust!");

    Ok(())
}

// Retrieve the config dir of Ibrowse (.../ibrowse)
#[pyfunction]
fn config_dir() -> PyResult<String> {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");

    Ok(config_dir.to_string_lossy().into_owned())
}

// Retrieve the cache dir of Ibrowse (.../ibrowse/cache)
#[pyfunction]
fn cache_dir() -> PyResult<String> {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse")
        .join("cache");

    Ok(config_dir.to_string_lossy().into_owned())
}

// Get passwords (as a Python dict '{url, [username, password]}')
#[pyfunction]
fn passwords() -> PyResult<HashMap<String, [String; 2]>> {
    let config = load_config();

    Ok(config.passwords)
}

// Get bookmarks (as a Python dict '{url, name}')
#[pyfunction]
fn bookmarks() -> PyResult<HashMap<String, String>> {
    let config = load_config();

    Ok(config.bookmarks)
}

// Get previous tabs (as a Python list '[url]')
#[pyfunction]
fn previous_tabs() -> PyResult<Vec<String>> {
    let config = load_config();

    Ok(config.previous_tabs)
}

// Get preferred browser (as a Python string '[browser_name]')
#[pyfunction]
fn preferred_browser() -> PyResult<String> {
    let config = load_config();

    Ok(config.preferred_browser)
}

// Append a password object with url, username, and password to config.json
#[pyfunction]
fn add_password(url: &str, username: &str, password: &str) -> PyResult<()> {
    let mut config = load_config();
    let array = [username.to_string(), password.to_string()];
    config.passwords.insert(url.to_string(), array);

    save_config(&config);
    Ok(())
}

// Remove a password object with specified url from config.json
#[pyfunction]
fn remove_password(url: &str) -> PyResult<()> {
    let mut config = load_config();
    config.passwords.remove(url);

    save_config(&config);
    Ok(())
}

// Append a bookmark object with url and bookmark name to config.json
#[pyfunction]
fn add_bookmark(url: &str, name: &str) -> PyResult<()> {
    let mut config = load_config();
    config.bookmarks.insert(url.to_string(), name.to_string());

    save_config(&config);
    Ok(())
}

// Remove a bookmark object with the specified bookmark name from config.json
#[pyfunction]
fn remove_bookmark(name: &str) -> PyResult<()> {
    let mut config = load_config();
    config.bookmarks.remove(name);

    save_config(&config);
    Ok(())
}

// Set the previous tabs array to a Python list ('[url]')
#[pyfunction]
fn set_previous_tabs(tabs: Vec<String>) -> PyResult<()> {
    let mut config = load_config();
    config.previous_tabs = tabs;

    save_config(&config);
    Ok(())
}

// Set the preferred browser to a Python string ('[browser_name]')
#[pyfunction]
fn set_preferred_browser(browser: String) -> PyResult<()> {
    let mut config = load_config();
    config.preferred_browser = browser;

    save_config(&config);
    Ok(())
}

// Open an HTML in UTF-8 encoding and return a Python string of the contents
#[pyfunction]
fn read_html(file_name: &str) -> PyResult<String> {
    let mut file = fs::File::open(file_name).map_err(
        |e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file: {}", e)))?;
    let mut contents = String::new();

    file.read_to_string(&mut contents).map_err(
        |e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e)))?;
    Ok(contents)
}

// Define the module and wrap functions
#[pymodule]
fn ibrowse(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, py)?)?;
    m.add_function(wrap_pyfunction!(config_dir, py)?)?;
    m.add_function(wrap_pyfunction!(cache_dir, py)?)?;
    m.add_function(wrap_pyfunction!(passwords, py)?)?;
    m.add_function(wrap_pyfunction!(bookmarks, py)?)?;
    m.add_function(wrap_pyfunction!(previous_tabs, py)?)?;
    m.add_function(wrap_pyfunction!(preferred_browser, py)?)?;
    m.add_function(wrap_pyfunction!(add_password, py)?)?;
    m.add_function(wrap_pyfunction!(remove_password, py)?)?;
    m.add_function(wrap_pyfunction!(add_bookmark, py)?)?;
    m.add_function(wrap_pyfunction!(remove_bookmark, py)?)?;
    m.add_function(wrap_pyfunction!(set_previous_tabs, py)?)?;
    m.add_function(wrap_pyfunction!(set_preferred_browser, py)?)?;
    m.add_function(wrap_pyfunction!(read_html, py)?)?;
    Ok(())
}
