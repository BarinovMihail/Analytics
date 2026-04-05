import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/layouts/AppLayout";
import { DashboardPage } from "@/pages/DashboardPage";
import { UploadPage } from "@/pages/UploadPage";
import { UploadsPage } from "@/pages/UploadsPage";
import { UploadErrorsPage } from "@/pages/UploadErrorsPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "upload", element: <UploadPage /> },
      { path: "uploads", element: <UploadsPage /> },
      { path: "uploads/:batchId/errors", element: <UploadErrorsPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
