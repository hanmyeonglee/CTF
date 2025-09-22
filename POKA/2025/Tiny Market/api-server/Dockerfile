# Use the latest official Rust image as the base image
FROM rust:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the binary
COPY . ./

# Make the binary executable
RUN chmod +x /app/target/release/api-server

# Create necessary directories and files
RUN touch chall.db

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["./target/release/api-server"]