// publish-fdp.ts runs under vite-node from an FDPlight checkout. It lives
// outside that checkout, so vite's file-system restriction is lifted.
export default { server: { fs: { strict: false } } };
