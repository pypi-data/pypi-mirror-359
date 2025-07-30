# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'main'
BUILD_TIME = '2025-07-02T19:08:37Z'
BUILD_COMMIT = '50af58d96de9505ec9be36a3262359a9e70bef0c'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
