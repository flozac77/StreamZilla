// Runs once on first MongoDB startup (mounted into /docker-entrypoint-initdb.d/).
// Creates an application user scoped to the app database with readWrite only.
// Root credentials are provided via MONGO_INITDB_ROOT_USERNAME / MONGO_INITDB_ROOT_PASSWORD.

const appDb = process.env.MONGO_APP_DB;
const appUser = process.env.MONGO_APP_USERNAME;
const appPassword = process.env.MONGO_APP_PASSWORD;

if (!appDb || !appUser || !appPassword) {
    throw new Error(
        "MONGO_APP_DB, MONGO_APP_USERNAME and MONGO_APP_PASSWORD must be set " +
        "in the environment when initializing MongoDB."
    );
}

db = db.getSiblingDB(appDb);
db.createUser({
    user: appUser,
    pwd: appPassword,
    roles: [{ role: "readWrite", db: appDb }],
});
