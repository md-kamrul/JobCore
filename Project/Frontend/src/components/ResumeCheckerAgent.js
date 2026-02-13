// ResumeCheckerAgent: detects resume/cv/checker keywords and returns a recommendation string if needed
export function getResumeCheckerRecommendation(message) {
  const lower = message.toLowerCase();
  // Robustly match 'curriculum vitae' (any case, any spacing)
  const cvRegex = /curriculum\s*vitae/i;
  if (
    lower.includes("resume") ||
    lower.includes("cv") ||
    lower.includes("checker") ||
    cvRegex.test(message)
  ) {
    return "💡 If you want to check or improve your resume, try our website's Resume Checker option!";
  }
  return "";
}
