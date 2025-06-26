import ApiError from "../utils/apiError.js";

const methodNotAllowed = (req, res) => {
  throw ApiError.methodNotAllowed(
    `Method ${req.method} not allowed on ${req.originalUrl}`
  );
};

export default methodNotAllowed;
