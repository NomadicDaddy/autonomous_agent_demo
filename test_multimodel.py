"""
Tests for multi-model configuration.
"""

import sys
from unittest.mock import patch


def test_default_model():
    """Test that default model is used when no overrides specified."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test']):
        # Import after patching argv
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.model == aidd_c.DEFAULT_MODEL
        assert args.init_model is None
        assert args.code_model is None

        # Compute effective models (same logic as in main())
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        assert init_model == aidd_c.DEFAULT_MODEL
        assert code_model == aidd_c.DEFAULT_MODEL


def test_single_model_override():
    """Test that --model overrides both init and code."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test', '--model', 'custom-model']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.model == 'custom-model'
        assert args.init_model is None
        assert args.code_model is None

        # Compute effective models
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        assert init_model == 'custom-model'
        assert code_model == 'custom-model'


def test_init_model_override():
    """Test that --init-model overrides only init phase."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test', '--init-model', 'init-model']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.model == aidd_c.DEFAULT_MODEL
        assert args.init_model == 'init-model'
        assert args.code_model is None

        # Compute effective models
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        assert init_model == 'init-model'
        assert code_model == aidd_c.DEFAULT_MODEL


def test_code_model_override():
    """Test that --code-model overrides only coding phase."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test', '--code-model', 'code-model']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.model == aidd_c.DEFAULT_MODEL
        assert args.init_model is None
        assert args.code_model == 'code-model'

        # Compute effective models
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        assert init_model == aidd_c.DEFAULT_MODEL
        assert code_model == 'code-model'


def test_both_overrides():
    """Test that --init-model and --code-model can be used together."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test',
                                     '--init-model', 'haiku', '--code-model', 'opus']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.init_model == 'haiku'
        assert args.code_model == 'opus'

        # Compute effective models
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        assert init_model == 'haiku'
        assert code_model == 'opus'


def test_overrides_take_precedence():
    """Test that --init-model and --code-model take precedence over --model."""
    with patch.object(sys, 'argv', ['prog', '--project-dir', './test',
                                     '--model', 'base-model',
                                     '--init-model', 'haiku',
                                     '--code-model', 'opus']):
        import importlib
        import aidd_c
        importlib.reload(aidd_c)

        args = aidd_c.parse_args()

        assert args.model == 'base-model'
        assert args.init_model == 'haiku'
        assert args.code_model == 'opus'

        # Compute effective models
        init_model = args.init_model if args.init_model else args.model
        code_model = args.code_model if args.code_model else args.model

        # Specific overrides take precedence
        assert init_model == 'haiku'
        assert code_model == 'opus'


if __name__ == "__main__":
    test_default_model()
    test_single_model_override()
    test_init_model_override()
    test_code_model_override()
    test_both_overrides()
    test_overrides_take_precedence()

    print("All multi-model configuration tests passed!")
