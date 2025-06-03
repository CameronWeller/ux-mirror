# UX-Mirror

A Python-based user experience analysis and visualization platform.

## Project Structure

```
ux-mirror/
├── agents/              # Agent-based analysis components
├── src/                # Core source code
├── tests/              # Test suites
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Dependencies

- Python 3.8+
- See requirements.txt for full list

## Development Guidelines

1. All UX-Mirror code should be contained within this project
2. Python code should follow PEP 8 style guidelines
3. Use virtual environments for development
4. Maintain clear separation from the Vulkan project

## Integration with C++ Vulkan HIP Engine

The C++ Vulkan HIP Engine is a separate project that provides graphics capabilities. When integrating:
1. Use the provided API interfaces
2. Do not modify the Vulkan project's C++ code directly
3. Maintain clear separation of concerns
4. Use the build system to manage dependencies

## Building and Running

1. Set up Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python start_core_system.py
   ```

## Testing

```powershell
python -m pytest tests/
```

## License

[Your License Here] 