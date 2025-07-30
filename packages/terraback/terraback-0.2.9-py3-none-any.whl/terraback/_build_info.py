# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2123'
BUILD_TIME = '2025-07-01T21:23:32Z'
BUILD_COMMIT = '833dacd365be3e3d73beaf020eedd674c19755fe'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
