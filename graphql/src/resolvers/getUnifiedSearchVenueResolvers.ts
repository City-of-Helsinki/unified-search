import type { AccessibilityProfileType } from '../datasources/es/types.js';
import type { VenueProps } from '../types.js';

export function getUnifiedSearchVenueResolvers() {
  return {
    name({ venue }: VenueProps) {
      return venue.name;
    },
    description({ venue }: VenueProps) {
      return venue.description;
    },
    location({ venue }: VenueProps) {
      return venue.location;
    },
    openingHours({ venue }: VenueProps) {
      return venue.openingHours;
    },
    images({ venue }: VenueProps) {
      return venue.images;
    },
    ontologyWords({ venue }: VenueProps) {
      return venue.ontologyWords;
    },
    serviceOwner({ venue }: VenueProps) {
      return venue.serviceOwner;
    },
    reservation({ venue }: VenueProps) {
      return venue.reservation;
    },
    targetGroups({ venue }: VenueProps) {
      return venue.targetGroups;
    },
    accessibility({ venue }: VenueProps) {
      return venue.accessibility;
    },
    accessibilityShortcomingFor(
      { venue }: VenueProps,
      args: { profile?: AccessibilityProfileType }
    ) {
      if (args.profile) {
        const shortcoming = venue.accessibility.shortcomings.filter(
          (shortcoming) => shortcoming.profile === args.profile
        );
        if (shortcoming && shortcoming.length > 0) {
          return shortcoming[0];
        }
      }
      return undefined;
    },
    meta({ venue }: VenueProps) {
      return venue.meta;
    },
    isCultureAndLeisureDivisionVenue({ venue }: VenueProps) {
      return venue.isCultureAndLeisureDivisionVenue ?? false;
    },
  };
}
