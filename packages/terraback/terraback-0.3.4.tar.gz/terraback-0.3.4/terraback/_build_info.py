# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'main'
BUILD_TIME = '2025-07-02T21:03:38Z'
BUILD_COMMIT = '2e6ba39961b38e0437feeaa67effabd64d8fd012'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
