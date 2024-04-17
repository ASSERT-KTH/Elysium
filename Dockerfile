FROM python:3.8

# Set environment variables for Rust installation
ENV RUST_VERSION nightly

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    ~/.cargo/bin/rustup toolchain install $RUST_VERSION && \
    ~/.cargo/bin/rustup override set $RUST_VERSION && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# Install graphviz
RUN apt-get update && apt-get install -y graphviz

# Set the working directory in the container
WORKDIR /Elysium

# Copy the Python application code
COPY elysium elysium
COPY evaluation evaluation
COPY run_on_smartbugs.py run_on_smartbugs.py

RUN mkdir smartbugs && mkdir results

# Install dependencies
RUN cd elysium && pip install -r requirements.txt
RUN solc-select install 0.4.26 && solc-select use 0.4.26

CMD [ "python3", "run_on_smartbugs.py", "smartbugs", "results" ]