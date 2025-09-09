/**
 * Converts a string from a datetime-local input (YYYY-MM-DDTHH:mm)
 * into a full UTC ISO 8601 string (YYYY-MM-DDTHH:mm:ss.sssZ).
 * This function avoids the ambiguities of the new Date(string) constructor
 * by manually parsing the components and creating a local date object
 * from them, which is then converted to UTC.
 *
 * @param {string | null | undefined} localDateTimeString The date string to convert.
 * @returns {string | null} The UTC ISO string, or null if the input is invalid.
 */
export function localDateTimeStringToUTCISO(localDateTimeString) {
  if (!localDateTimeString || typeof localDateTimeString !== 'string') {
    return null;
  }

  // The expected format is YYYY-MM-DDTHH:mm
  const parts = localDateTimeString.match(
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/
  );

  if (!parts) {
    console.error(`Invalid localDateTimeString format: "${localDateTimeString}"`);
    return null;
  }

  // Note: parts[0] is the full match.
  const year = parseInt(parts[1], 10);
  const month = parseInt(parts[2], 10);
  const day = parseInt(parts[3], 10);
  const hours = parseInt(parts[4], 10);
  const minutes = parseInt(parts[5], 10);

  // The month for the Date constructor is 0-indexed (0-11).
  const monthIndex = month - 1;

  // Create a new Date object using the components. This constructor
  // interprets the components in the local timezone of the browser.
  const localDate = new Date(year, monthIndex, day, hours, minutes);

  // A simple validity check. If the date object created doesn't match the input
  // components, it means an invalid date (like Feb 30) was "corrected" by the
  // Date constructor, which we don't want.
  if (
    localDate.getFullYear() !== year ||
    localDate.getMonth() !== monthIndex ||
    localDate.getDate() !== day
  ) {
    console.error(`Invalid date components created from string: "${localDateTimeString}"`);
    return null;
  }

  // Convert the local date to its UTC ISO string representation.
  return localDate.toISOString();
}
