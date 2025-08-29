import { getTodayString } from '../utils.js';

export function getOpeningHoursResolvers() {
  return {
    today({ data }: unknown) {
      const openingHoursToday = data.find(
        (openingHoursDay) => openingHoursDay.date === getTodayString()
      );
      return openingHoursToday ? openingHoursToday.times : [];
    },
  };
}
