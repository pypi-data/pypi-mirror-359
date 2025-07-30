# CDK Tutor

A CLI application that teaches AWS CDK to users through interactive challenges.

## Installation

With `pip`:

```bash
pip install cdk-tutor
```

With `pipx`:

```bash
pipx install cdk-tutor
```

With `uvx`:

```bash
uvx install cdk-tutor
```

## Usage

### List available challenges

```bash
cdk-tutor list-challenges
```

### Start a challenge

```bash
cdk-tutor start [CHALLENGE_NAME]
```

If you don't specify a challenge name, you'll be prompted to choose from available challenges.

### Grade a completed challenge

```bash
cdk-tutor grade [CHALLENGE_DIR]
```

## Features

- Interactive CLI with rich text formatting
- Step-by-step challenges to learn AWS CDK
- Automatic grading of solutions
- Detailed feedback to help users improve

## Challenge Structure

Each challenge includes:

- Starter code with TODOs to complete
- Clear instructions in a README
- Expected CloudFormation output for grading
- Solution files for reference

## Development

To add new challenges:

1. Create a new challenge in `src/cdk_tutor/challenges/`
2. Follow the `Challenge` model structure
3. Add your challenge to the list in `get_available_challenges()`

## License

MIT
