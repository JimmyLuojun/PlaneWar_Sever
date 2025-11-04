- always run codes via Poetry.
- answer me with necessary content without redundant content.
- this is the The Event_Driven Standard Order:""1. **Module docstring** (what this file does)
2. **Imports** (dependencies)
3. **Constants & Global Setup
4. **Asset & Resource Loading**(A dedicated section (or function) to load all assets (images, sounds, fonts) into memory.)
5. **Helper Functions** (module-level utilities)
6. **Class & Object Definitions**(If using OOP) Define all "actors" or "widgets" here.
7. **Core Application Initialization**(The code that "starts" the program and creates the main window or application object.)
8. **Event Handler Functions (The "Callbacks")**(Not all handlers must be functions — in OOP designs, they can be _methods_ bound to objects)
9. **Event Listeners / Bindings**(The "wiring" that connects a specific event to its handler function)
10. **Main Event Loop (`while True` or `app.mainloop()`)**()""
- this is the The Procedural Standard Order:""
1. **Module docstring** (what this file does)
2. **Imports** (dependencies)
3. **Constants** (module-level configuration)
4. **Helper Functions** (module-level utilities)
5. **Orchestration Functions** (Core Logic)
6. **Main Function** (The "Entry Point")
7. **`if __name__ == "__main__":` Block""
- this is the OOP Standard Order:""
1. **Module docstring** (what this file does)
2. **Imports** (dependencies)
3. **Type Definitions** (NewTypes, TypeVars, Protocols)
4. **Constants** (module-level configuration)
5. **Exceptions** (custom error hierarchy)
6. **[[Abstract Base Classes]]** (interfaces/protocols)
7. **Data Classes** (simple data containers)
8. **Helper Functions** (module-level utilities)
9. **Concrete Classes** (implementations)
    - Base classes first
    - Subclasses after their parents
    - Related classes together
10. **Factory Functions** (class construction helpers)
11. **Public API Functions** (convenience wrappers)
12. **Main** (if it's a script)""
- this is the Procedural Standard Order:""
1. **Module docstring** (what this file does)
2. **Imports** (dependencies)
3. **Type Definitions** (if using [[Type Hints]])
4. **Constants** (configuration)
5. **[[Exceptions]]** (if custom errors)
6. **[[Data Models]]** (if using dataclasses/models)
7. **[[Helper Functions]]** (private utilities)
8. **Core Logic** (main functionality)
9. **Public API** (what users call)
10. **Main** (if it's a script)""
- when creating pytest codes for files, creating them by AAA pattern.