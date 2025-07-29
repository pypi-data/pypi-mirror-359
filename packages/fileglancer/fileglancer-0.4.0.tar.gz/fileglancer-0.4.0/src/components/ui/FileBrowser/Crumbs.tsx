import React, { ReactNode } from 'react';
import {
  BreadcrumbLink,
  Breadcrumb,
  Typography,
  BreadcrumbSeparator
} from '@material-tailwind/react';
import {
  ChevronRightIcon,
  SlashIcon,
  Squares2X2Icon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router';

import { useFileBrowserContext } from '@/contexts/FileBrowserContext';
import { makeBrowseLink, makePathSegmentArray, joinPaths } from '@/utils';

export default function Crumbs(): ReactNode {
  const { currentFileSharePath, currentFolder } = useFileBrowserContext();

  const dirArray = makePathSegmentArray(currentFolder?.path || '');
  // Add the current file share path name as the first segment in the array
  dirArray.unshift(currentFileSharePath?.name || '');
  const dirDepth = dirArray.length;

  return (
    <div className="w-full py-2 px-3">
      <Breadcrumb className="bg-transparent p-0">
        <div className="flex items-center gap-1 h-5">
          <Squares2X2Icon className="icon-default text-primary-light" />
          <ChevronRightIcon className="icon-default" />
        </div>

        {/* Path segments */}
        {dirArray.map((pathSegment, index) => {
          if (currentFileSharePath) {
            const path = joinPaths(...dirArray.slice(1, index + 1));
            const link = makeBrowseLink(currentFileSharePath.name, path);

            if (index < dirDepth - 1) {
              // Render a breadcrumb link for each segment in the parent path
              return (
                <React.Fragment key={pathSegment + '-' + index}>
                  <BreadcrumbLink
                    as={Link}
                    to={link}
                    variant="text"
                    className="rounded-md hover:bg-primary-light/20 hover:!text-black focus:!text-black transition-colors cursor-pointer"
                  >
                    <Typography
                      variant="small"
                      className="font-medium text-primary-light"
                    >
                      {pathSegment}
                    </Typography>
                  </BreadcrumbLink>
                  {/* Add separator since is not the last segment */}
                  <BreadcrumbSeparator>
                    <SlashIcon className="icon-default" />
                  </BreadcrumbSeparator>
                </React.Fragment>
              );
            } else {
              // Render the last path component as text only
              return (
                <React.Fragment key={pathSegment + '-' + index}>
                  <Typography className="font-medium text-primary-default">
                    {pathSegment}
                  </Typography>
                </React.Fragment>
              );
            }
          }
        })}
      </Breadcrumb>
    </div>
  );
}
