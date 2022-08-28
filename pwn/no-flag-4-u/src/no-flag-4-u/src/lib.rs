//! # No Flag 4 U
//! 
//! Provides wrappers for some libc functions to mitigate security risks.
//! 
//! ## Features
//! 
//! - Memory is never freed after `__libc_start_main()` to prevent UAF.
//! - Safely wraps non-constant format strings.
//! - Panics on invalid UTF-8 strings in stdin or stdout.
//! - Stack buffer overflow protections.
//! - Logs IO to a file using an external process.
//! 
//! ### Wrappers
//! 
//! - read (WIP)
//! - write
//! - gets (WIP)
//! - puts
//! - scanf (TODO)
//! - printf
//! - heap
//! 
//! ## Build
//! 
//! Compile with:
//! 
//! ```
//! cargo build --release
//! ```
//! 
//! Currently supports `x86_64-unknown-linux-gnu` and `i686-unknown-linux-gnu`.
//! 
//! ### Options
//! 
//! By default, this library aims to provide as much safety as possible without breaking most programs.
//! However, in some cases it may be desirable to disable or enable certain mitigations.
//! 
//! Enable or disable optional features by passing flags to rustc:
//! 
//! ```
//! cargo build --features [OPTION]
//! ```
//! | OPTION                         | Description                                                     |
//! |--------------------------------|-----------------------------------------------------------------|
//! | `enable_restrict_n_directive`  | disallow `%n` conversion specifiers in format strings           |
//! | `enable_env_config`            | (TODO) allow overriding config options using env vars           |
//! | `enable_restrictive_seccomp`   | (TODO) immediately call seccomp to restrict dangerous syscalls  |
//! | `disable_read_hooks`           | do not hook functions belonging to the `read` family            |
//! | `disable_write_hooks`          | do not hook functions belonging to the `write` family           |
//! | `disable_gets_hooks`           | do not hook functions belonging to the `gets` family            |
//! | `disable_puts_hooks`           | do not hook functions belonging to the `puts` family            |
//! | `disable_scanf_hooks`          | do not hook functions belonging to the `scanf` family           |
//! | `disable_printf_hooks`         | do not hook functions belonging to the `printf` family          |
//! | `disable_heap_hooks`           | do not hook functions for managing dynamic memory               |
//! 
//! ## Usage
//! 
//! Call `ld.so` with the `--preload` flag (only affects the original process):
//! 
//! ```bash
//! ld.so --preload libno_flag_4_u.so [COMMAND]
//! ```
//! 
//! OR
//! 
//! Set the `LD_PRELOAD` environment variable (affects child processes):
//! 
//! ```bash
//! export LD_PRELOAD=libno_flag_4_u.so
//! [COMMAND]
//! ```
//! 
//! ### Logging
//! 
//! A TCP listener must be active to receive logs.
//! One is provided in the `log_server` binary, however, a custom program may also be used.
//! 
//! By default, logs are stored relative to the cwd of the `log_server` process.
//! 
//! ### Configuration
//! 
//! The config file is located at `/etc/no-flag-4-u/settings.conf` (TODO)

#![feature(iter_advance_by)]
#![feature(panic_update_hook)]
#![feature(local_key_cell_methods)]
#![feature(c_variadic)]

mod config;
pub mod preload_hooks;
mod utils;

use std::sync::atomic::AtomicBool;

/// Returns `true` if `__libc_start_main` has been run.
/// Returns `false` otherwise.
static MAIN_STARTED: AtomicBool = AtomicBool::new(false);
