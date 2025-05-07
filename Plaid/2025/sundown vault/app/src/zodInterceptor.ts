// From https://github.com/gajus/slonik?tab=readme-ov-file#result-parser-interceptor
import { type Interceptor, type QueryResultRow, SchemaValidationError } from "slonik";

export const createResultParserInterceptor = (): Interceptor => {
	return {
		// If you are not going to transform results using Zod, then you should use `afterQueryExecution` instead.
		// Future versions of Zod will provide a more efficient parser when parsing without transformations.
		// You can even combine the two – use `afterQueryExecution` to validate results, and (conditionally)
		// transform results as needed in `transformRow`.
		transformRow: async (executionContext, actualQuery, row) => {
			const { log, resultParser } = executionContext;

			if (!resultParser) {
				return row;
			}

			// It is recommended (but not required) to parse async to avoid blocking the event loop during validation
			const validationResult = await resultParser.safeParseAsync(row);

			if (!validationResult.success) {
				throw new SchemaValidationError(actualQuery, row, validationResult.error.issues);
			}

			return validationResult.data as QueryResultRow;
		},
	};
};
