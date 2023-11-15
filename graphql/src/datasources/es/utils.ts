import type { TermField, ArrayFilter } from './types';

export function buildArrayFilter(
  field: TermField,
  values: string[] = []
): ArrayFilter[] {
  if (values.length === 0) {
    return [];
  }

  return [
    {
      bool: {
        should: values.map((value) => ({
          term: {
            [field]: value,
          },
        })),
      },
    },
  ];
}
