import { upperCase } from 'lodash-es';

export function getBackgroundColor(letter: string) {
  switch (letter.toUpperCase()) {
    case 'A':
    case 'À':
    case 'Á':
    case 'Â':
    case 'Ä':
    case 'Æ':
    case 'Ã':
    case 'Å':
    case 'Ā':
      return '#E06055';
    case 'B':
      return '#ED6192';
    case 'C':
    case 'Ç':
    case 'Ć':
    case 'Č':
      return '#BA68C8';
    case 'D':
      return '#9575CD';
    case 'E':
    case 'È':
    case 'É':
    case 'Ê':
    case 'Ë':
    case 'Ē':
    case 'Ė':
    case 'Ę':
      return '#7986CB';
    case 'F':
      return '#5E97F6';
    case 'G':
      return '#4FC3F7';
    case 'H':
      return '#58D0E1';
    case 'I':
    case 'Î':
    case 'Ï':
    case 'Í':
    case 'Ī':
    case 'Į':
    case 'Ì':
      return '#4FB6AC';
    case 'J':
      return '#57BB8A';
    case 'K':
      return '#9CCC65';
    case 'L':
    case 'Ł':
      return '#D4E157';
    case 'M':
      return '#FDD835';
    case 'N':
    case 'Ñ':
    case 'Ń':
      return '#F6BF32';
    case 'O':
    case 'Ô':
    case 'Ö':
    case 'Ò':
    case 'Ó':
    case 'Œ':
    case 'Ø':
    case 'Ō':
    case 'Õ':
      return '#F5A631';
    case 'P':
      return '#F18864';
    case 'Q':
      return '#C2C2C2';
    case 'R':
      return '#90A4AE';
    case 'S':
      return '#A1887F';
    case 'T':
      return '#A3A3A3';
    case 'U':
    case 'Û':
    case 'Ü':
    case 'Ù':
    case 'Ú':
    case 'Ū':
      return '#AFB6E0';
    case 'V':
      return '#B39DDB';
    case 'W':
      return '#C2C2C2';
    case 'X':
      return '#80DEEA';
    case 'Y':
    case 'Ÿ':
      return '#BCAAA4';
    case 'Z':
    case 'Ž':
    case 'Ź':
    case 'Ż':
      return '#AED581';
    default:
      return 'var(--mat-sys-outline-variant)';
  }
}

export function getFirstLetter(from: string | null | undefined) {
  const letter = from && from.trim().length >= 1 ? upperCase(from.trim().slice(0, 1)) : '';
  if (letter && !isNaN(Number(letter))) {
    return '#';
  }
  return letter;
}

export function getStyle(from: string | null | undefined, size: number) {
  return {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: getBackgroundColor(getFirstLetter(from)),
  };
}
