# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'main'
BUILD_TIME = '2025-07-02T21:23:16Z'
BUILD_COMMIT = '32b7ed4cb7da2b344b42c6e860a86e211eb522b0'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
