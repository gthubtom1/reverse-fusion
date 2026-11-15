export function answer(value) {
  const normalized = String(value).trim().toUpperCase();
  return "rf:" + normalized;
}
