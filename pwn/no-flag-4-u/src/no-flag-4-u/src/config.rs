use std::{env, fs, path::PathBuf};

/// Contains the configuration.
#[derive(Debug, PartialEq, Eq)]
pub struct Config {
    /// The port that the log server listens on.
    /// Defaults to `40000`.
    pub port: u16,

    /// The host the log server is running on.
    /// Defaults to `127.0.0.1`
    pub host: String,

    /// Whether to log events.
    /// Defaults to `true`
    pub logging: bool,

    /// Directory to store log files.
    /// Defaults to `./log`
    pub log_dir: String,
}

/// Default config options.
impl Default for Config {
    /// Returns the default configuration.
    fn default() -> Config {
        Config {
            port: 40000,
            host: String::from("127.0.0.1"),
            logging: true,
            log_dir: String::from("./log"),
        }
    }
}

/// Returns a string containing the path to the config file.
fn get_config_path() -> String {
    let mut config_path = PathBuf::new();
    config_path.push("/etc/");
    config_path.push(env!("CARGO_PKG_NAME"));
    config_path.push("settings.conf");

    String::from(config_path.as_path().to_str().unwrap())
}

/// Parses a config file string and returns a `Config` struct.
fn parse_config(contents: String) -> Config {
    let mut conf = Config {
        ..Default::default()
    };

    for row in contents.lines() {
        let trimmed = row.trim();

        // configuration comment
        if trimmed.starts_with('#') {
            continue;
        }

        // empty line
        if trimmed.is_empty() {
            continue;
        }

        let (key, value) = trimmed
            .split_once(char::is_whitespace)
            .unwrap_or_else(|| panic!("failed parsing config:\n{row}"));

        match key {
            "PORT" => {
                conf.port = value
                    .parse::<u16>()
                    .unwrap_or_else(|e| panic!("failed parsing port:\n{row}\n{e}"));
            }
            "HOST" => {
                conf.host = String::from(value);
            }
            "LOGGING" => {
                conf.logging = value
                    .parse::<bool>()
                    .unwrap_or_else(|e| panic!("failed parsing logging setting:\n{row}\n{e}"));
            }
            "LOG_DIR" => {
                conf.log_dir = String::from(value);
            }
            _ => panic!("unrecognized configuration key: {key}"), // unrecognized option
        }
    }

    conf
}

/// Returns the current configuration.
pub fn read_config() -> Config {
    if let Ok(contents) = fs::read_to_string(get_config_path()) {
        parse_config(contents)
    } else {
        Config {
            ..Default::default()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty() {
        assert_eq!(
            parse_config(String::new()),
            Config {
                ..Default::default()
            }
        )
    }
}
