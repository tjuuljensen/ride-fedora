# Shared product facts, native installers

The Windows development catalog has `package.autopsy`, `package.cyberchef`,
and `package.networkminer`. Fedora's legacy library also names these tools.
The following facts can be reviewed together when the Linux operations are
migrated; neither platform should import the other's installer definition.

| Product | Shared facts to reconcile | Platform-owned facts |
| --- | --- | --- |
| Autopsy | Product ID, official homepage, upstream repository, Apache license and bundled notices. | Windows MSI asset and uninstall; Linux upstream setup, Java dependencies, user data and removal. Linux is a deferred candidate. |
| CyberChef | Product ID, GCHQ source, Apache license and retained notices. | Windows portable ZIP placement; Linux offline artifact location and browser integration. Fedora legacy function remains deferred. |
| NetworkMiner | Publisher identity, license terms, release metadata and architecture claims. | Windows package acquisition and installation; Linux runtime and packaging support. Fedora legacy function remains deferred. |

The first Linux v3 catalog also includes products not currently present in the
Windows catalog, such as exfatprogs, EWF tools and the Volatility3 core. A
future shared product-facts file could contain stable IDs, homepage, upstream
repository and license evidence. It should be generated into each platform's
native catalog only after both sides agree on meaning and maintenance owner.
Download endpoints, package manager names, target support, verification,
service settings and rollback remain platform-specific.

This staged approach avoids a runtime dependency between the repositories
while still catching identity and license drift in review.
