from serial_triggers import
import time

# List available ports
ports = SerialWriter.list_ports()
print(f"Available ports: {ports}")

# Create a SerialWriter instance
# Parameters: port_name, baud_rate, queue_behavior ("add", "discard", or "block")
writer = SerialWriter("COM8", 2000000, "add")

# Write an integer value to the serial port
writer.write(42)

# Write an integer value with a delay (in milliseconds)
writer.write_delayed(255, 500)  # Writes 255, waits 500ms, then writes 255 again

# Change queue behavior
writer.set_queue_behavior("discard")

# Get current queue behavior
behavior = writer.get_queue_behavior()
print(f"Current queue behavior: {behavior}")

# Write multiple values in sequence
for i in range(10):
    writer.write(i)
    time.sleep(0.1)

# Clean up when done
writer.close()
