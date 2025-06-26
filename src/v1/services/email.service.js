import fs from "fs";
import path from "path";
import handlebars from "handlebars";
import OTP from "../models/otp.model.js";
import { fileURLToPath } from "url";
import { dirname } from "path";
import { formatDate, generateOTP } from "../../lib/utils.js";
import { sendEmail } from "../../lib/nodemailer.config.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const templatesDir = path.join(__dirname, "..", "..", "templates");

const templatePaths = {
  otpTemplate: path.join(templatesDir, "OTPTemplate.html"),
};

const templates = Object.fromEntries(
  Object.entries(templatePaths).map(([key, filePath]) => [
    key,
    handlebars.compile(fs.readFileSync(filePath, "utf8")),
  ])
);

export async function sendOTPEmail(email, userName) {
  try {
    await OTP.findOneAndDelete({ email });
    const otp = generateOTP();
    await OTP.create({ email, otp });

    const subject = "OTP Request";
    const date = formatDate(new Date().toLocaleString());
    const emailText = `Hello ${userName},\n\nYour OTP is: ${otp}`;
    const html = templates.otpTemplate({ userName, otp, date });

    return sendEmail({ to: email, subject, text: emailText, html });
  } catch (error) {
    console.error("Error sending OTP:", error);
    throw ApiError.internalServerError("Failed to send OTP email");
  }
}

export default { sendOTPEmail };
