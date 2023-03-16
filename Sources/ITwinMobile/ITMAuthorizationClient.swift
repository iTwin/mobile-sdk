/*---------------------------------------------------------------------------------------------
* Copyright (c) Bentley Systems, Incorporated. All rights reserved.
* See LICENSE.md in the project root for license terms and full copyright notice.
*--------------------------------------------------------------------------------------------*/

import IModelJsNative

// MARK: - ITMAuthorizationClient protocol

/// Protocol that extends `AuthorizationClient` with convenience functionality. A default extension to this protocol implements both of the provided functions.
public protocol ITMAuthorizationClient: AuthorizationClient {
    /// The default domain to use in the ``createError(domain:code:reason:)-9oi8h``  function.
    var errorDomain: String { get }

    /// Creates and returns an NSError object with the specified settings.
    /// - Parameters:
    ///   - domain: The domain to use for the NSError, default to nil, which uses the value from ``errorDomain``.
    ///   - code: The code to use for the NSError, defaults 200.
    ///   - reason: The reason to use for the NSError's NSLocalizedFailureReasonErrorKey userInfo value
    /// - Returns: An NSError object with the specified values.
    func createError(domain: String?, code: Int, reason: String) -> NSError
    /// Call the `onAccessTokenChanged` callback from `AuthorizationClient`, if that callback is set.
    /// - Parameters:
    ///   - token: The current access token, or nil
    ///   - expirationDate: The expiration date for the current access token, or nil
    func raiseOnAccessTokenChanged(_ token: String?, _ expirationDate: Date?)
}

// MARK: - ITMAuthorizationClient extension with default implementations

/// Key used in the `userInfo` dict of errors created with `error(domain:code:reason:)`.
public let ITMAuthorizationClientErrorKey = "ITMAuthorizationClientErrorKey"

/// Extension that provides default implementation for the functions in the `ITMAuthorizationClient` protocol.
public extension ITMAuthorizationClient {
    /// Creates and returns an NSError object with the specified settings. Provides a default value `nil` for `domain` and a default value of `200` for `code`. The `nil` default value for domain causes it to use the value stored in ``errorDomain``.
    /// - Parameters:
    ///   - domain: The domain to use for the NSError, default to nil, which uses the value from ``errorDomain``.
    ///   - code: The code to use for the NSError, defaults 200.
    ///   - reason: The reason to use for the NSError's NSLocalizedFailureReasonErrorKey userInfo value
    /// - Returns: An NSError object with the specified values. Along with the other settings, the `userInfo` dictionary of the return value will contain a value of `true` for `ITMAuthorizationClientErrorKey`.
    func createError(domain: String? = nil, code: Int = 200, reason: String) -> NSError {
        return NSError(domain: domain ?? errorDomain, code: code, userInfo: [NSLocalizedFailureReasonErrorKey: reason, ITMAuthorizationClientErrorKey: true])
    }

    /// Calls the onAccessTokenChanged callback, if that callback is set.
    /// - Note: If either `token` or `expirationDate` is nil, it will be treated as if both are nil.
    /// - Parameters:
    ///   - token: The current access token, or nil
    ///   - expirationDate: The expiration date for the current access token, or nil
    func raiseOnAccessTokenChanged(_ token: String?, _ expirationDate: Date?) {
        if let onAccessTokenChanged = onAccessTokenChanged {
            if let token = token,
               let expirationDate = expirationDate {
                onAccessTokenChanged(token, expirationDate)
            } else {
                onAccessTokenChanged(nil, nil)
            }
        }
    }
}
