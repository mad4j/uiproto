# Makefile for HMI Protocol Buffer code generation

PROTO_FILE = hmi_protocol.proto
PROTO_DIR = .
OUT_DIR = generated

# Python output
PYTHON_OUT = $(OUT_DIR)/python

# JavaScript output
JS_OUT = $(OUT_DIR)/js

# Java output
JAVA_OUT = $(OUT_DIR)/java

# C++ output
CPP_OUT = $(OUT_DIR)/cpp

# Go output
GO_OUT = $(OUT_DIR)/go

# C# output
CSHARP_OUT = $(OUT_DIR)/csharp

.PHONY: all python javascript java cpp go csharp clean help

all: python javascript java cpp go csharp

help:
	@echo "HMI Protocol Code Generation"
	@echo "============================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Generate code for all languages"
	@echo "  python     - Generate Python code"
	@echo "  javascript - Generate JavaScript code"
	@echo "  java       - Generate Java code"
	@echo "  cpp        - Generate C++ code"
	@echo "  go         - Generate Go code"
	@echo "  csharp     - Generate C# code"
	@echo "  clean      - Remove generated files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - protoc (Protocol Buffer compiler)"
	@echo "  - Language-specific protoc plugins (for Go, etc.)"

python: $(PYTHON_OUT)
	@echo "Generating Python code..."
	protoc --proto_path=$(PROTO_DIR) --python_out=$(PYTHON_OUT) $(PROTO_FILE)
	@echo "✓ Python code generated in $(PYTHON_OUT)"

javascript: $(JS_OUT)
	@echo "Generating JavaScript code..."
	protoc --proto_path=$(PROTO_DIR) --js_out=import_style=commonjs,binary:$(JS_OUT) $(PROTO_FILE)
	@echo "✓ JavaScript code generated in $(JS_OUT)"

java: $(JAVA_OUT)
	@echo "Generating Java code..."
	protoc --proto_path=$(PROTO_DIR) --java_out=$(JAVA_OUT) $(PROTO_FILE)
	@echo "✓ Java code generated in $(JAVA_OUT)"

cpp: $(CPP_OUT)
	@echo "Generating C++ code..."
	protoc --proto_path=$(PROTO_DIR) --cpp_out=$(CPP_OUT) $(PROTO_FILE)
	@echo "✓ C++ code generated in $(CPP_OUT)"

go: $(GO_OUT)
	@echo "Generating Go code..."
	protoc --proto_path=$(PROTO_DIR) --go_out=$(GO_OUT) $(PROTO_FILE)
	@echo "✓ Go code generated in $(GO_OUT)"

csharp: $(CSHARP_OUT)
	@echo "Generating C# code..."
	protoc --proto_path=$(PROTO_DIR) --csharp_out=$(CSHARP_OUT) $(PROTO_FILE)
	@echo "✓ C# code generated in $(CSHARP_OUT)"

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(PYTHON_OUT): $(OUT_DIR)
	mkdir -p $(PYTHON_OUT)

$(JS_OUT): $(OUT_DIR)
	mkdir -p $(JS_OUT)

$(JAVA_OUT): $(OUT_DIR)
	mkdir -p $(JAVA_OUT)

$(CPP_OUT): $(OUT_DIR)
	mkdir -p $(CPP_OUT)

$(GO_OUT): $(OUT_DIR)
	mkdir -p $(GO_OUT)

$(CSHARP_OUT): $(OUT_DIR)
	mkdir -p $(CSHARP_OUT)

clean:
	@echo "Cleaning generated files..."
	rm -rf $(OUT_DIR)
	@echo "✓ Generated files removed"

# Run the Python example (requires generated Python code)
run-example: python
	@echo "Running Python example..."
	PYTHONPATH=$(PYTHON_OUT):$$PYTHONPATH python3 example_usage.py

# Validate the proto file
validate:
	@echo "Validating proto file..."
	protoc --decode_raw < /dev/null || protoc --python_out=/tmp $(PROTO_FILE)
	@echo "✓ Proto file is valid"
