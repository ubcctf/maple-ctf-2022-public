mod config;

use chrono::Local;
use libc::fork;
use rand::random;
use std::{
    fs::{create_dir_all, OpenOptions},
    io::{Read, Write},
    net::{Ipv4Addr, TcpListener, TcpStream},
    path::PathBuf,
};

/// Receives data from a TCP Stream.
/// Logs data to a file.
fn handle_connection(mut stream: TcpStream, conf: config::Config) {
    let timestamp = Local::now().to_rfc3339();

    let mut buf = Vec::new();
    let len = stream
        .read_to_end(&mut buf)
        .unwrap_or_else(|e| panic!("Error: {e}"));

    let s = String::from_utf8_lossy(&buf);
    let username = s.lines().next().expect("failed to get username");
    println!("Received {len} bytes from {username} at {timestamp}");

    let mut log_path = PathBuf::from(conf.log_dir);
    log_path.push(username);
    create_dir_all(&log_path).expect("failed to create log directory");

    log_path.push(format!(
        "{timestamp}#{discriminator}",
        discriminator = random::<u16>()
    ));
    let mut log_file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(log_path)
        .expect("failed to create log file");
    log_file.write_all(&buf).expect("failed to write log data");
}

/// Binds to port, forks on connections.
fn main() {
    let conf = config::read_config();

    if !conf.logging {
        panic!("logging is disabled, check  configuration file");
    }

    let listener = TcpListener::bind((Ipv4Addr::new(127, 0, 0, 1), conf.port))
        .expect("failed to bind to port");

    for connection in listener.incoming() {
        match connection {
            Ok(stream) => {
                // SAFETY: parent process immediately closes file descriptor
                //         child process immediately drops listener
                let child = unsafe { fork() };
                match child {
                    -1 => {
                        panic!();
                    }
                    0 => {
                        drop(listener);
                        handle_connection(stream, conf);
                        break;
                    }
                    _ => (),
                }
            }
            Err(e) => {
                println!("Error: {e}");
            }
        }
    }
}
