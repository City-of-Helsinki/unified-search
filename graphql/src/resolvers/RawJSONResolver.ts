export function RawJSONResolver() {
  return {
    data(parent: unknown) {
      // Testing and debugging only
      return JSON.stringify(parent);
    },
  };
}
