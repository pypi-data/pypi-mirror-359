# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2056'
BUILD_TIME = '2025-07-01T20:56:33Z'
BUILD_COMMIT = '0bcca35e8560774e023bec2ae61de202be2f0538'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
