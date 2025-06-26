import otpGenerator from "otp-generator";

export function formatDate(dateString) {
  // Helper function to get the ordinal suffix
  function getOrdinalSuffix(day) {
    if (day > 3 && day < 21) return "th";
    switch (day % 10) {
      case 1:
        return "st";
      case 2:
        return "nd";
      case 3:
        return "rd";
      default:
        return "th";
    }
  }

  // Create a Date object from the ISO 8601 string
  const date = new Date(dateString);

  const day = date.getUTCDate();
  const monthName = date.toLocaleString("en-US", { month: "long" });
  const year = date.getUTCFullYear();
  const dayWithSuffix = `${day}${getOrdinalSuffix(day)}`;

  return `${dayWithSuffix} ${monthName} ${year}`;
}

export function generateOTP() {
  const otp = otpGenerator.generate(4, {
    upperCaseAlphabets: false,
    lowerCaseAlphabets: false,
    specialChars: false,
  });

  return otp;
}

export const paginate = async ({
  model,
  query = {},
  page = 1,
  limit = 10,
  sort = { createdAt: -1 },
  populateOptions = [],
  select = [],
  excludeById = null,
  excludeField = "_id",
}) => {
  const skip = (page - 1) * limit;

  if (excludeById !== null) {
    query[excludeField] = { $ne: excludeById };
  }

  let queryBuilder = model
    .find(query)
    .skip(skip)
    .limit(limit)
    .sort(sort)
    .select(select);

  populateOptions.forEach((option) => {
    queryBuilder = queryBuilder.populate(option);
  });

  const documents = await queryBuilder;

  const totalCount = await model.countDocuments();
  const filteredCount = await model.countDocuments(query);
  const totalPages = Math.ceil(filteredCount / limit);

  return {
    documents,
    pagination: {
      totalCount,
      filteredCount,
      totalPages,
      page,
      limit,
    },
  };
};
