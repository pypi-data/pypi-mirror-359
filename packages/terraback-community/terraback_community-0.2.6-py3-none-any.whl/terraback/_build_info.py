# Build information - tier is determined at runtime based on license
BUILD_EDITION = 'universal'  # Single build for all tiers
VERSION = 'dev-20250701-2031'
BUILD_TIME = '2025-07-01T20:31:58Z'
BUILD_COMMIT = '9b32b6b3c253482da4e5e100f022fda3139eb2a7'

# License tiers are determined at runtime by checking the license
# This allows the same binary to work with different license tiers
AVAILABLE_TIERS = ['free', 'pro', 'enterprise']
