import { DateTime } from 'luxon';
import { DEFAULT_TIME_ZONE } from '../../../constants';
import type {
  ArrayFilter,
  MustHaveReservableResourceFilter,
  OpenAtFilter,
} from '../../../types';
import type { QueryResultFilterProps } from '../types';
import { buildArrayFilter } from '../../../utils';

/**
 * @deprecated
 *
 * TODO: Reservable is still needed and should be re-implemented in https://helsinkisolutionoffice.atlassian.net/browse/LIIKUNTA-578.
 */
// const buildMustHaveReservableResourceFilter =
//   (): MustHaveReservableResourceFilter => ({
//     bool: {
//       should: [
//         // i.e. OR
//         {
//           term: {
//             'venue.resources.reservable': true,
//           },
//         },
//         {
//           exists: {
//             field: 'venue.resources.externalReservationUrl',
//           },
//         },
//       ],
//     },
//   });

export function getFilters({
  administrativeDivisionIds,
  ontologyTreeIdOrSets,
  ontologyWordIdOrSets,
  providerTypes,
  serviceOwnerTypes,
  targetGroups,
  mustHaveReservableResource,
  openAt,
}: QueryResultFilterProps): Array<
  ArrayFilter | OpenAtFilter | MustHaveReservableResourceFilter
> {
  // Assume time zone DEFAULT_TIME_ZONE when there is no time zone offset provided by the client.
  const openAtDateTime = DateTime.fromISO(openAt ?? '', {
    zone: DEFAULT_TIME_ZONE,
  });
  const finalOpenAt = openAtDateTime.isValid ? openAtDateTime.toISO() : openAt;

  return [
    ...buildArrayFilter(
      'venue.location.administrativeDivisions.id.keyword',
      administrativeDivisionIds ?? []
    ),
    ...(ontologyTreeIdOrSets ?? []).flatMap((ontologyTreeIdOrSet) =>
      buildArrayFilter(
        'links.raw_data.ontologytree_ids_enriched.id',
        ontologyTreeIdOrSet ?? []
      )
    ),
    ...(ontologyWordIdOrSets ?? []).flatMap((ontologyWordIdOrSet) =>
      buildArrayFilter(
        'links.raw_data.ontologyword_ids_enriched.id',
        ontologyWordIdOrSet ?? []
      )
    ),
    ...buildArrayFilter(
      'venue.serviceOwner.providerType.keyword',
      providerTypes ?? []
    ),
    ...buildArrayFilter(
      'venue.serviceOwner.type.keyword',
      serviceOwnerTypes ?? []
    ),
    ...buildArrayFilter('venue.targetGroups.keyword', targetGroups ?? []),
    // TODO: Reservable is still needed and should be re-implemented in https://helsinkisolutionoffice.atlassian.net/browse/LIIKUNTA-578.
    // ...(mustHaveReservableResource
    //   ? [buildMustHaveReservableResourceFilter()]
    //   : []),
    ...(finalOpenAt
      ? [
          {
            term: {
              'venue.openingHours.openRanges': finalOpenAt,
            },
          },
        ]
      : []),
  ];
}

export function filterQuery(query: any, filterProps: QueryResultFilterProps) {
  const filters = getFilters(filterProps);
  if (filters.length > 0) {
    query.query.bool.minimum_should_match = 1;
    query.query.bool.filter = filters;
  }
}
