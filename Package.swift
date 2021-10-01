// swift-tools-version:5.3
// The swift-tools-version declares the minimum version of Swift required to build this package.

/*---------------------------------------------------------------------------------------------
* Copyright (c) Bentley Systems, Incorporated. All rights reserved.
* See LICENSE.md in the project root for license terms and full copyright notice.
*--------------------------------------------------------------------------------------------*/

import PackageDescription

let package = Package(
    name: "itwin-mobile-sdk",
    platforms: [
        .iOS("12.2"),
    ],
    products: [
        // Products define the executables and libraries a package produces, and make them visible to other packages.
        .library(
            name: "ITwinMobile",
            targets: ["ITwinMobile"]),
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
        // .package(url: /* package url */, from: "1.0.0"),
        .package(url: "https://github.com/iTwin/mobile-ios-package", .exact("2.19.18")),
        .package(url: "https://github.com/mxcl/PromiseKit", from: "6.15.3"),
        .package(name: "PMKFoundation", url: "https://github.com/PromiseKit/Foundation.git", from: "3.0.0"),
        // The following is a fork of CoreLocation that changes the iOS platform to v9
        .package(name: "PMKCoreLocation", url: "https://github.com/fallingspirit/CoreLocation", from: "3.1.2"),
        .package(name: "Reachability", url: "https://github.com/ashleymills/Reachability.swift", from: "5.1.0"),
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages this package depends on.
        .target(
            name: "ITwinMobile",
            dependencies: [
                .product(name: "IModelJsNative", package: "mobile-ios-package"),
                .product(name: "PromiseKit", package: "PromiseKit"),
                .product(name: "PMKFoundation", package: "PMKFoundation"),
                .product(name: "PMKCoreLocation", package: "PMKCoreLocation"),
                .product(name: "Reachability", package: "Reachability"),
            ],
            resources: [
                .process("ITwinMobile.docc")
            ]),
//        .testTarget(
//            name: "ITwinMobileTests",
//            dependencies: ["ITwinMobile"]),
    ]
)
