use std::process::{Command, Stdio};
use std::thread;

#[derive(Debug)]
pub struct WorkerResult {
    pub worker_id: usize,
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
}

pub struct WorkerPool {
    workers: Vec<WorkerHandle>,
}

struct WorkerHandle {
    id: usize,
    handle: thread::JoinHandle<WorkerResult>,
}

impl Default for WorkerPool {
    fn default() -> Self {
        Self::new()
    }
}

impl WorkerPool {
    pub fn new() -> Self {
        Self {
            workers: Vec::new(),
        }
    }

    pub fn spawn_worker(
        &mut self,
        worker_id: usize,
        program: String,
        initial_args: Vec<String>,
        tests: Vec<String>,
        pytest_args: Vec<String>,
    ) {
        let handle = thread::spawn(move || {
            let mut cmd = Command::new(&program);

            for arg in initial_args {
                cmd.arg(arg);
            }

            for test in tests {
                cmd.arg(test);
            }

            for arg in pytest_args {
                cmd.arg(arg);
            }

            cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

            match cmd.output() {
                Ok(output) => WorkerResult {
                    worker_id,
                    exit_code: output.status.code().unwrap_or(-1),
                    stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                    stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                },
                Err(e) => WorkerResult {
                    worker_id,
                    exit_code: -1,
                    stdout: String::new(),
                    stderr: format!("Failed to execute command: {e}"),
                },
            }
        });

        self.workers.push(WorkerHandle {
            id: worker_id,
            handle,
        });
    }

    pub fn wait_for_all(self) -> Vec<WorkerResult> {
        let mut results = Vec::new();

        for worker in self.workers {
            match worker.handle.join() {
                Ok(result) => results.push(result),
                Err(_) => {
                    results.push(WorkerResult {
                        worker_id: worker.id,
                        exit_code: -1,
                        stdout: String::new(),
                        stderr: "Worker thread panicked".to_string(),
                    });
                }
            }
        }

        results.sort_by_key(|r| r.worker_id);
        results
    }

    #[allow(dead_code)]
    pub fn worker_count(&self) -> usize {
        self.workers.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_worker_pool_creation() {
        let pool = WorkerPool::new();
        assert_eq!(pool.worker_count(), 0);
    }

    #[test]
    fn test_worker_result_creation() {
        let result = WorkerResult {
            worker_id: 1,
            exit_code: 0,
            stdout: "test output".to_string(),
            stderr: String::new(),
        };
        assert_eq!(result.worker_id, 1);
        assert_eq!(result.exit_code, 0);
        assert_eq!(result.stdout, "test output");
    }

    #[test]
    fn test_spawn_and_wait_echo_command() {
        let mut pool = WorkerPool::new();

        // Use echo command for testing
        pool.spawn_worker(
            0,
            "echo".to_string(),
            vec![],
            vec!["hello".to_string()],
            vec!["world".to_string()],
        );

        assert_eq!(pool.worker_count(), 1);

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].worker_id, 0);
        assert_eq!(results[0].exit_code, 0);
        assert!(results[0].stdout.contains("hello"));
        assert!(results[0].stdout.contains("world"));
    }

    #[test]
    fn test_multiple_workers() {
        let mut pool = WorkerPool::new();

        // Spawn multiple echo workers
        pool.spawn_worker(
            0,
            "echo".to_string(),
            vec![],
            vec!["worker0".to_string()],
            vec![],
        );

        pool.spawn_worker(
            1,
            "echo".to_string(),
            vec![],
            vec!["worker1".to_string()],
            vec![],
        );

        assert_eq!(pool.worker_count(), 2);

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 2);

        // Results should be sorted by worker_id
        assert_eq!(results[0].worker_id, 0);
        assert_eq!(results[1].worker_id, 1);
        assert!(results[0].stdout.contains("worker0"));
        assert!(results[1].stdout.contains("worker1"));
    }

    #[test]
    fn test_worker_failure() {
        let mut pool = WorkerPool::new();

        // Use a command that should fail
        pool.spawn_worker(
            0,
            "false".to_string(), // Command that always exits with code 1
            vec![],
            vec![],
            vec![],
        );

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].worker_id, 0);
        assert_ne!(results[0].exit_code, 0); // Should be non-zero exit code
    }

    #[test]
    fn test_worker_with_initial_args() {
        let mut pool = WorkerPool::new();

        // Test with initial args (like "python -m pytest")
        pool.spawn_worker(
            0,
            "echo".to_string(),
            vec!["initial".to_string(), "args".to_string()],
            vec!["test1".to_string()],
            vec!["final".to_string()],
        );

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].exit_code, 0);

        let output = &results[0].stdout;
        assert!(output.contains("initial"));
        assert!(output.contains("args"));
        assert!(output.contains("test1"));
        assert!(output.contains("final"));
    }

    #[test]
    fn test_worker_invalid_command() {
        let mut pool = WorkerPool::new();

        // Use a command that doesn't exist
        pool.spawn_worker(
            0,
            "nonexistent_command_12345".to_string(),
            vec![],
            vec![],
            vec![],
        );

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].worker_id, 0);
        assert_eq!(results[0].exit_code, -1);
        assert!(results[0].stderr.contains("Failed to execute command"));
    }

    #[test]
    fn test_worker_result_sorting() {
        let mut pool = WorkerPool::new();

        // Spawn workers in reverse order
        pool.spawn_worker(
            2,
            "echo".to_string(),
            vec![],
            vec!["worker2".to_string()],
            vec![],
        );

        pool.spawn_worker(
            0,
            "echo".to_string(),
            vec![],
            vec!["worker0".to_string()],
            vec![],
        );

        pool.spawn_worker(
            1,
            "echo".to_string(),
            vec![],
            vec!["worker1".to_string()],
            vec![],
        );

        let results = pool.wait_for_all();
        assert_eq!(results.len(), 3);

        // Should be sorted by worker_id regardless of spawn order
        assert_eq!(results[0].worker_id, 0);
        assert_eq!(results[1].worker_id, 1);
        assert_eq!(results[2].worker_id, 2);
    }

    #[test]
    fn test_empty_worker_pool() {
        let pool = WorkerPool::new();
        let results = pool.wait_for_all();
        assert!(results.is_empty());
    }
}
