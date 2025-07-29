# Frequenz Client Common Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- The metrics and components enums `.from_proto()` are deprecated, please use the new `enum_from_proto()` instead.
- Some minimum dependencies have been bumped, you might need to update your minimum dependencies too:

    * `frequenz-api-common` to 0.6.1
    * `frequenz-core` to 1.0.2

## New Features

- A new module `frequenz.client.common.enum_proto` has been added, which provides a generic `enum_from_proto()` function to convert protobuf enums to Python enums.
- The `frequenz.client.common.microgrid.ComponentCategory` was extended to include the missing categories.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
