<!-- START Adjust URL -->
![Solution passing all tests](https://img.shields.io/github/actions/workflow/status/Blockly2Java/Template/test-solution.yml?branch=main&label=Solution%20passing%20all%20tests)
![Template compiling successfully](https://img.shields.io/github/actions/workflow/status/Blockly2Java/Template/test-template.yml?branch=main&label=Template%20compiling%20successfully)
<!-- END Adjust URL -->

## Abstract

<!-- START Adjust for exercise -->
This exercise focuses on modeling the interaction between two objects (human and dog) and implementing coordinated movement behavior. Students practice object-oriented concepts including constructor design, reference attributes to manage inter-object relationships, getter methods for state access, and motion logic with boundary awareness in a bounded world. The implementation also covers random movement generation and method decomposition for behavior coordination. The difficulty level is intermediate, building on foundational shape and motion concepts from previous exercises.
<!-- END Adjust for exercise -->

Detailed exercise instructions can be found in the README file of the template repository.

## Local Setup

To set up the workspace for local development:

1. Clone this repository into a new folder:
   ```bash
   git clone git@github.com:Blockly2Java/Template.git MyExercise
   ```
2. Navigate into the cloned folder and run the setup script:
   ```bash
   cd MyExercise
   ./local-setup.sh
   ```

The script will automatically restructure the directory layout:
- Moves this repository (with its git history) into a `parent/` subdirectory.
- Copies IDE settings and configuration files from `root-template/` to the workspace root.
- Clones/updates the sibling repositories (`template`, `solution`, `tests`) alongside `parent/`.

Resulting folder structure:
```text
MyExercise/
├── VS-Code.code-workspace  # Copied from root-template
├── parent/                 # This repository (git repo)
├── template/               # Student code template (git repo)
├── solution/               # Reference solution (git repo)
└── tests/                  # Test harness (git repo)
```

## Exporting to Artemis

This repository generates a ZIP file that can be directly imported into Artemis.

### Local Export


1. Ensure the workspace is set up (run `./local-setup.sh` if needed)
2. Run the export command: `<exercise-name>` must match the Repository-Name
   ```bash
   ./parent/.github/scripts/local-export.sh --name <exercise-name>
   ```

3. The ZIP file is created in the `Artemis_Export/` directory
4. Import the ZIP into Artemis via the exercise creation/edit UI

### GitHub Export

The export runs automatically on GitHub when code is pushed to any branch. Download the generated ZIP from the workflow artifacts and import it into Artemis.
