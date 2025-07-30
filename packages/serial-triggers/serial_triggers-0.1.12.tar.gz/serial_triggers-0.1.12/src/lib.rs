use crossbeam::channel::{unbounded, Receiver, Sender};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use serialport::SerialPort;
use std::thread;
use std::time::{Duration, Instant};
use thread_priority::ThreadPriority;

#[derive(Clone, Copy, PartialEq)]
enum QueueBehavior {
    Add,
    Discard,
}

enum ThreadCommand {
    WriteValue(u8),
    WriteDelayed(u8, Duration),
    Shutdown,
}

#[pyclass]
struct SerialTriggerWriter {
    sender: Sender<ThreadCommand>,
}

#[pymethods]
impl SerialTriggerWriter {
    #[new]
    #[pyo3(signature = (port_name, baud_rate, queue_behavior=None))]
    /// Create a new serial trigger writer.
    fn new(port_name: &str, baud_rate: u32, queue_behavior: Option<&str>) -> PyResult<Self> {
        let behavior = match queue_behavior {
            None => QueueBehavior::Add,
            Some("add") => QueueBehavior::Add,
            Some("discard") => QueueBehavior::Discard,
            _ => {
                return Err(PyValueError::new_err(
                    "Queue behavior must be 'add' or 'discard'",
                ))
            }
        };

        // Create channel for thread communication
        let (sender, receiver) = unbounded();

        // Open the serial port in the main thread
        let port = serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(1000))
            .open()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to open serial port: {}", e)))?;

        // Spawn the worker thread with ownership of the port
        thread::spawn(move || {
            // Set thread priority to Max
            if let Err(e) = thread_priority::set_current_thread_priority(ThreadPriority::Max) {
                eprintln!(
                    "Failed to set thread priority: {}. Please report this issue.",
                    e
                );
            }
            process_commands(port, receiver, behavior);
        });

        Ok(SerialTriggerWriter { sender })
    }

    #[pyo3(signature = (value, delay=None))]
    /// Write a value to the serial port. Optionally, delay the write by a specified amount of time (in seconds).
    fn write(&self, value: u8, delay: Option<f64>) -> PyResult<()> {
        let command = match delay {
            Some(delay) => ThreadCommand::WriteDelayed(value, Duration::from_secs_f64(delay)),
            None => ThreadCommand::WriteValue(value),
        };

        // Always add to queue
        self.sender
            .send(command)
            .map_err(|_| PyRuntimeError::new_err("Failed to send command to worker thread"))?;

        Ok(())
    }

    /// Close the serial port and stop the worker thread.
    fn close(&mut self) -> PyResult<()> {
        // Send shutdown command to the worker thread
        let _ = self.sender.send(ThreadCommand::Shutdown);
        Ok(())
    }

    #[staticmethod]
    /// List available serial ports.
    fn list_ports() -> PyResult<Vec<String>> {
        let ports = serialport::available_ports()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to list serial ports: {}", e)))?;

        let port_names = ports.into_iter().map(|info| info.port_name).collect();

        Ok(port_names)
    }

    fn __enter__(slf: PyRef<Self>) -> PyResult<Py<Self>> {
        // return self
        Ok(slf.into())
    }

    fn __exit__(
        mut slf: PyRefMut<Self>,
        exc_type: Bound<'_, crate::PyAny>,
        exc_value: Bound<'_, crate::PyAny>,
        traceback: Bound<'_, crate::PyAny>,
    ) -> PyResult<()> {
        // close the serial port
        slf.close()?;
        Ok(())
    }
}

fn process_commands(
    mut port: Box<dyn SerialPort>,
    receiver: Receiver<ThreadCommand>,
    queue_behavior: QueueBehavior,
) {
    loop {
        // Try to receive a command with timeout
        match receiver.recv_timeout(Duration::from_millis(100)) {
            Ok(command) => {
                match command {
                    ThreadCommand::WriteValue(value) => {
                        // Convert the integer to bytes (assuming little-endian)
                        let bytes = value.to_le_bytes();

                        // Write the bytes to the serial port
                        if let Err(e) = port.write(&bytes) {
                            eprintln!("Failed to write to serial port: {}", e);
                        }

                        port.flush().unwrap();
                    }
                    ThreadCommand::WriteDelayed(value, delay) => {
                        // Convert the integer to bytes (assuming little-endian)
                        let bytes = value.to_le_bytes();

                        // Wait for the exact amount of time
                        let start = Instant::now();
                        while start.elapsed() < delay {
                            // Spin wait for precise timing
                            std::hint::spin_loop();
                        }

                        // Write the same value again after the delay
                        if let Err(e) = port.write(&bytes) {
                            eprintln!("Failed to write delayed value to serial port: {}", e);
                        }

                        port.flush().unwrap();
                    }
                    ThreadCommand::Shutdown => {
                        // Exit the loop and terminate the thread
                        break;
                    }
                }

                // For discard behavior, we need to drain the queue
                if queue_behavior == QueueBehavior::Discard {
                    while let Ok(_command) = receiver.try_recv() {
                        dbg!("Discarding command");
                    }
                }
            }
            Err(crossbeam::channel::RecvTimeoutError::Timeout) => {
                // Continue the loop if no command was received
            }
            Err(crossbeam::channel::RecvTimeoutError::Disconnected) => {
                // Exit the loop and terminate the thread
                break;
            }
        }

        // Sleep a bit to avoid busy waiting
        thread::sleep(Duration::from_micros(1));
    }
}

#[pymodule]
fn serial_triggers(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SerialTriggerWriter>()?;
    Ok(())
}
