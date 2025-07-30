# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2025'
BUILD_TIME = '2025-07-01T20:25:29Z'
BUILD_COMMIT = '5ffb6306c7e7ee166fb10e6362d24abeb27f6424'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
